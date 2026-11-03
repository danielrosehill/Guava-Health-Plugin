#!/usr/bin/env python3
"""Guava Health API client for agents. Standard library only (Python 3.9+).

One OAuth grant = one Guava profile. The account holder grants once for
themselves and once per dependent (choosing the dependent on Guava's consent
screen). Each grant is stored under a local profile label, e.g. "me", "child".

Credentials come from the environment, never from files in this repo:
  GUAVA_CLIENT_ID, GUAVA_CLIENT_SECRET   (required)
  GUAVA_REDIRECT_URI   default https://localhost:8765/callback
  GUAVA_ENV            live | test  (default: test if the client id starts guava_test_)
  GUAVA_HOME           default ~/.config/guava-health  (tokens live here, 0600)

All output is JSON on stdout. Errors are JSON on stderr with exit code 1.
See docs/api-notes.md for the endpoint reference this follows.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import http.server
import json
import os
import secrets
import ssl
import subprocess
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

API_BASE = {"live": "https://api.guavahealth.com", "test": "https://api-test.guavahealth.com"}
AUTHORIZE_URL = "https://guavahealth.com/oauth/authorize"
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCOPES_FILE = REPO_ROOT / "reference" / "scopes-full.txt"

DATA_ENTRY_TYPES = {
    "med_usage", "symptoms", "bowel_movement", "journal", "mood", "energy",
    "menstrual_cycle", "sexual_activity",
}
METRIC_TYPES = {
    "resting_heart_rate", "heart_rate_variability", "oxygen_saturation", "respiratory_rate",
    "steps", "heart_rate", "vo2_max", "weight", "height", "systolic_blood_pressure",
    "diastolic_blood_pressure", "blood_glucose", "body_temperature", "body_fat",
    "body_water", "bone_mass", "muscle_mass", "lean_mass",
}
SEARCH_RESOURCES = {"metrics", "sleep", "activities", "nutrition", "water"}
FHIR_RESOURCES = {
    "Patient", "Practitioner", "AllergyIntolerance", "Condition", "Procedure",
    "MedicationRequest", "Immunization",
}


# ---------------------------------------------------------------- helpers

def die(msg: str, **extra) -> None:
    print(json.dumps({"error": msg, **extra}, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)


def out(obj) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def env(name: str, default: str | None = None, required: bool = False) -> str:
    v = os.environ.get(name) or default
    if required and not v:
        die(f"{name} is not set", hint="Export it, or run through your secrets wrapper.")
    return v  # type: ignore[return-value]


def home() -> Path:
    p = Path(env("GUAVA_HOME", str(Path.home() / ".config" / "guava-health")))
    (p / "tokens").mkdir(parents=True, exist_ok=True)
    os.chmod(p, 0o700)
    return p


USER_AGENT = "guava-health-plugin/0.1 (+https://github.com/danielrosehill/Guava-Health-Plugin)"


def guava_env() -> str:
    """GUAVA_ENV if set; else infer from the client id (guava_test_client_... -> test)."""
    e = os.environ.get("GUAVA_ENV")
    if e:
        return e
    return "test" if os.environ.get("GUAVA_CLIENT_ID", "").startswith("guava_test_") else "live"


def api_base() -> str:
    e = guava_env()
    if e not in API_BASE:
        die("GUAVA_ENV must be live or test")
    return API_BASE[e]


def client_auth_header() -> str:
    cid = env("GUAVA_CLIENT_ID", required=True)
    sec = env("GUAVA_CLIENT_SECRET", required=True)
    return "Basic " + base64.b64encode(f"{cid}:{sec}".encode()).decode()


def http(method: str, url: str, *, form: dict | None = None, body: dict | None = None,
         headers: dict | None = None) -> dict:
    # Cloudflare in front of Guava answers 403 "error code: 1010" to the default
    # Python-urllib User-Agent (tested 2026-11-03), so always send our own.
    h = {"Accept": "application/json", "User-Agent": USER_AGENT, **(headers or {})}
    data = None
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        h["Content-Type"] = "application/x-www-form-urlencoded"
    elif body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return json.loads(raw) if raw.strip() else {"status": r.status}
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            detail = json.loads(raw)
        except ValueError:
            detail = raw[:2000]
        die(f"HTTP {e.code} from {method} {urllib.parse.urlsplit(url).path}", detail=detail)
    return {}


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def iso(value: str | None) -> str:
    """Accept 'now', an ISO datetime with or without offset; return ISO with offset."""
    if not value or value == "now":
        return now_iso()
    try:
        t = dt.datetime.fromisoformat(value)
    except ValueError:
        die(f"Not an ISO 8601 datetime: {value}")
    if t.tzinfo is None:
        t = t.astimezone()  # local timezone
    return t.isoformat(timespec="seconds")


# ---------------------------------------------------------------- token store

def token_path(profile: str) -> Path:
    if not profile.replace("-", "").replace("_", "").isalnum():
        die("Profile label must be alphanumeric (dash/underscore allowed)")
    return home() / "tokens" / f"{profile}.json"


def save_token(profile: str, tok: dict) -> None:
    tok = dict(tok)
    tok["obtained_at"] = int(dt.datetime.now().timestamp())
    tok["env"] = guava_env()
    p = token_path(profile)
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(tok, f, indent=2)


def load_token(profile: str) -> dict:
    p = token_path(profile)
    if not p.exists():
        die(f"No grant stored for profile '{profile}'",
            hint=f"Run: guava.py auth --profile {profile}")
    return json.loads(p.read_text())


def access_token(profile: str) -> str:
    tok = load_token(profile)
    age = dt.datetime.now().timestamp() - tok.get("obtained_at", 0)
    if age < tok.get("expires_in", 3600) - 120:
        return tok["access_token"]
    if not tok.get("refresh_token"):
        die(f"Access token for '{profile}' expired and no refresh token (offline_access not granted)",
            hint=f"Run: guava.py auth --profile {profile}")
    # Refresh tokens rotate: persist the new pair before using either.
    new = http("POST", api_base() + "/oauth/token",
               form={"grant_type": "refresh_token", "refresh_token": tok["refresh_token"]},
               headers={"Authorization": client_auth_header()})
    for k in ("profile_id", "profile_name"):
        if k in tok:
            new.setdefault(k, tok[k])
    save_token(profile, new)
    return new["access_token"]


def api(profile: str, method: str, path: str, **kw) -> dict:
    h = {"Authorization": "Bearer " + access_token(profile), "Accept-Encoding": "identity"}
    return http(method, api_base() + path, headers=h, **kw)


# ---------------------------------------------------------------- auth flow

def ensure_cert() -> tuple[Path, Path]:
    d = home() / "localhost-cert"
    d.mkdir(exist_ok=True)
    crt, key = d / "cert.pem", d / "key.pem"
    if not crt.exists():
        try:
            subprocess.run(
                ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "3650",
                 "-subj", "/CN=localhost", "-keyout", str(key), "-out", str(crt)],
                check=True, capture_output=True)
        except (OSError, subprocess.CalledProcessError):
            die("openssl is needed for the local https callback", hint="Or use auth --paste")
        os.chmod(key, 0o600)
    return crt, key


def wait_for_callback(redirect_uri: str, timeout: int) -> str:
    u = urllib.parse.urlsplit(redirect_uri)
    if u.hostname not in ("localhost", "127.0.0.1"):
        die("Local callback only works for a localhost redirect URI", hint="Use auth --paste")
    got: dict = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            if urllib.parse.urlsplit(self.path).path != u.path:
                self.send_response(404); self.end_headers(); return
            got["url"] = f"https://{u.netloc}{self.path}"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<p>Guava authorisation received. You can close this tab.</p>")

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer((u.hostname, u.port or 443), H)
    crt, key = ensure_cert()
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(str(crt), str(key))
    srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
    srv.timeout = 1
    end = dt.datetime.now().timestamp() + timeout
    while "url" not in got and dt.datetime.now().timestamp() < end:
        srv.handle_request()
    srv.server_close()
    if "url" not in got:
        die("Timed out waiting for the redirect", hint="Retry, or use auth --paste")
    return got["url"]


def pending_path(profile: str) -> Path:
    d = home() / "pending"
    d.mkdir(exist_ok=True)
    return d / f"{profile}.json"


def start_flow(a) -> dict:
    redirect_uri = env("GUAVA_REDIRECT_URI", "https://localhost:8765/callback")
    scopes = a.scopes or " ".join(Path(a.scopes_file).read_text().split())
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(24)
    # Tested 2026-11-03: PAR needs response_type=code and client_id in the body even
    # with Basic auth (neither is in Guava's docs).
    par = http("POST", api_base() + "/oauth/par", form={
        "response_type": "code", "client_id": env("GUAVA_CLIENT_ID", required=True),
        "code_challenge": challenge, "code_challenge_method": "S256", "scope": scopes,
        "state": state, "redirect_uri": redirect_uri,
    }, headers={"Authorization": client_auth_header()})
    url = AUTHORIZE_URL + "?" + urllib.parse.urlencode(
        {"client_id": env("GUAVA_CLIENT_ID"), "request_uri": par["request_uri"]})
    pend = {"verifier": verifier, "state": state, "redirect_uri": redirect_uri,
            "expires_at": int(dt.datetime.now().timestamp()) + int(par.get("expires_in", 600))}
    fd = os.open(pending_path(a.profile), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(pend, f)
    return {"step": "open_consent", "profile": a.profile, "url": url,
            "expires_in_seconds": int(par.get("expires_in", 600)),
            "instruction": ("Open the URL, sign in as the account holder and, on the consent "
                            f"screen, choose the profile for '{a.profile}' (yourself or a dependent). "
                            "You land on the redirect URI; if that page fails to load, copy the "
                            f"full address and run: guava.py auth -p {a.profile} --finish '<url>'")}


def finish_flow(profile: str, returned: str) -> None:
    pp = pending_path(profile)
    if not pp.exists():
        die(f"No pending authorisation for '{profile}'", hint=f"Run: guava.py auth -p {profile} --start")
    pend = json.loads(pp.read_text())
    q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(returned.strip()).query))
    if "error" in q:
        die("Authorisation refused", detail=q)
    if q.get("state") != pend["state"]:
        die("State mismatch: discard this redirect and start again")
    tok = http("POST", api_base() + "/oauth/token", form={
        "grant_type": "authorization_code", "code": q["code"], "code_verifier": pend["verifier"],
        "redirect_uri": pend["redirect_uri"],
    }, headers={"Authorization": client_auth_header()})
    pp.unlink()
    save_token(profile, tok)
    # /v1/me is documented under a "profile" scope that the app form does not offer
    # (2026-11-03); try it, but don't fail the grant if it is refused.
    try:
        me = api(profile, "GET", "/v1/me")
    except SystemExit:
        me = {"unavailable": "GET /v1/me refused; see stderr"}
    if isinstance(me, dict) and me.get("profile"):
        tok = load_token(profile)
        tok["profile_id"] = me["profile"].get("id")
        tok["profile_name"] = " ".join(filter(None, [me["profile"].get("given_name"),
                                                      me["profile"].get("family_name")]))
        save_token(profile, tok)
    out({"ok": True, "profile": profile, "granted_scopes": tok.get("scope", "").split(),
         "patient": tok.get("patient"), "me": me})


def cmd_auth(a) -> None:
    """Default: one go with a local https listener. --start / --finish split it in two
    so the consent screen can be opened on any device (phone, another machine) and the
    final URL pasted back, which also suits agents that can't hold stdin open."""
    if a.finish:
        finish_flow(a.profile, a.finish); return
    info = start_flow(a)
    if a.start:
        out(info); return
    print(json.dumps(info, indent=2), file=sys.stderr)
    if not a.no_browser:
        webbrowser.open(info["url"])
    pend = json.loads(pending_path(a.profile).read_text())
    if a.paste:
        returned = input("Paste the full URL you were redirected to: ")
    else:
        returned = wait_for_callback(pend["redirect_uri"], a.timeout)
    finish_flow(a.profile, returned)


def cmd_profiles(a) -> None:
    rows = []
    for p in sorted((home() / "tokens").glob("*.json")):
        t = json.loads(p.read_text())
        rows.append({"label": p.stem, "guava_profile": t.get("profile_name"),
                     "profile_id": t.get("profile_id"), "env": t.get("env"),
                     "has_refresh_token": bool(t.get("refresh_token")),
                     "scope_count": len(t.get("scope", "").split())})
    out(rows)


def cmd_me(a) -> None:
    out(api(a.profile, "GET", "/v1/me"))


def cmd_revoke(a) -> None:
    tok = load_token(a.profile)
    for k in ("refresh_token", "access_token"):
        if tok.get(k):
            http("POST", api_base() + "/oauth/revoke", form={"token": tok[k]},
                 headers={"Authorization": client_auth_header()})
    token_path(a.profile).unlink()
    out({"ok": True, "revoked": a.profile})


# ---------------------------------------------------------------- writes

def ident(entry: dict, key: str | None) -> dict:
    if key:
        entry["identifier"] = [{"value": key, "system": "guava-health-plugin"}]
    return entry


def post_entries(profile: str, type_: str, entries: list[dict], dry: bool) -> None:
    body = {"type": type_, "entries": entries}
    if dry:
        out({"dry_run": True, "POST": "/v1/data-entries", "body": body}); return
    out(api(profile, "POST", "/v1/data-entries", body=body))


def cmd_log_med(a) -> None:
    e = {"time": iso(a.time), "medication_name": a.name}
    if a.quantity is not None:
        e["quantity"] = a.quantity
    if a.notes:
        e["notes"] = a.notes
    post_entries(a.profile, "med_usage", [ident(e, a.id)], a.dry_run)


def cmd_log(a) -> None:
    if a.type not in DATA_ENTRY_TYPES:
        die(f"type must be one of {sorted(DATA_ENTRY_TYPES)}")
    e = {"time": iso(a.time)}
    for kv in a.field or []:
        k, _, v = kv.partition("=")
        if k == "tags":
            e[k] = [t.strip() for t in v.split(",") if t.strip()]
        else:
            try:
                e[k] = json.loads(v)
            except ValueError:
                e[k] = v
    if a.notes:
        e["notes"] = a.notes
    post_entries(a.profile, a.type, [ident(e, a.id)], a.dry_run)


def cmd_metric(a) -> None:
    if a.type not in METRIC_TYPES:
        die(f"type must be one of {sorted(METRIC_TYPES)}")
    e = {"type": a.type, "value": a.value, "time": iso(a.time)}
    if a.unit:
        e["unit"] = a.unit
    if a.method:
        e["method"] = a.method
    body = {"source": a.source, "log_type": "manual", "entries": [ident(e, a.id)]}
    if a.dry_run:
        out({"dry_run": True, "POST": "/v1/metrics", "body": body}); return
    out(api(a.profile, "POST", "/v1/metrics", body=body))


def cmd_write_raw(a) -> None:
    body = json.load(sys.stdin if a.body == "-" else open(a.body))
    if a.dry_run:
        out({"dry_run": True, "POST": a.path, "body": body}); return
    out(api(a.profile, "POST", a.path, body=body))


# ---------------------------------------------------------------- reads

def cmd_search(a) -> None:
    if a.resource not in SEARCH_RESOURCES:
        die(f"resource must be one of {sorted(SEARCH_RESOURCES)}")
    form = {}
    if a.types:
        form["types"] = a.types
    if a.start:
        form["start_time"] = iso(a.start)
    if a.end:
        form["end_time"] = iso(a.end)
    form["_count"] = str(a.count)
    res = api(a.profile, "POST", f"/v1/{a.resource}/_search", form=form)
    entries = list(res.get("entries", []))
    pages = 1
    nxt = next((l["url"] for l in res.get("link", []) if l.get("relation") == "next"), None)
    while nxt and a.all and pages < a.max_pages:
        # Next links are absolute and must be POSTed as-is with no body.
        res = http("POST", nxt, headers={"Authorization": "Bearer " + access_token(a.profile)})
        entries += res.get("entries", [])
        pages += 1
        nxt = next((l["url"] for l in res.get("link", []) if l.get("relation") == "next"), None)
    out({"resource": a.resource, "count": len(entries), "pages": pages,
         "more": bool(nxt), "entries": entries})


def cmd_fhir(a) -> None:
    if a.resource not in FHIR_RESOURCES:
        die(f"resource must be one of {sorted(FHIR_RESOURCES)}")
    path = f"/fhir/R4/{a.resource}" + (f"/{a.id}" if a.id else "")
    out(api(a.profile, "GET", path))


# ---------------------------------------------------------------- cli

def main() -> None:
    p = argparse.ArgumentParser(prog="guava.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def prof(sp, required=True):
        sp.add_argument("--profile", "-p", required=required,
                        help="local label of the grant, e.g. me, child")
        return sp

    s = prof(sub.add_parser("auth", help="grant access for one Guava profile"))
    s.add_argument("--scopes", help="space-separated scope string (default: reference/scopes-full.txt)")
    s.add_argument("--scopes-file", default=str(DEFAULT_SCOPES_FILE))
    s.add_argument("--paste", action="store_true", help="paste the redirect URL instead of running a local listener")
    s.add_argument("--start", action="store_true", help="only print the consent URL and save the pending state")
    s.add_argument("--finish", metavar="URL", help="complete a --start with the URL you were redirected to")
    s.add_argument("--no-browser", action="store_true")
    s.add_argument("--timeout", type=int, default=300)
    s.set_defaults(fn=cmd_auth)

    sub.add_parser("profiles", help="list stored grants").set_defaults(fn=cmd_profiles)
    prof(sub.add_parser("me", help="GET /v1/me")).set_defaults(fn=cmd_me)
    prof(sub.add_parser("revoke", help="revoke and forget a grant")).set_defaults(fn=cmd_revoke)

    s = prof(sub.add_parser("log-med", help="log a medication dose (med_usage)"))
    s.add_argument("--name", required=True)
    s.add_argument("--quantity", type=float)
    s.add_argument("--time", default="now")
    s.add_argument("--notes")
    s.add_argument("--id", help="idempotency key; reusing it makes Guava ignore the entry")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_log_med)

    s = prof(sub.add_parser("log", help="write a self-reported data entry"))
    s.add_argument("--type", required=True, help=", ".join(sorted(DATA_ENTRY_TYPES)))
    s.add_argument("--field", "-f", action="append", help="key=value, e.g. symptom_name=Cough, severity=4, tags=a,b")
    s.add_argument("--time", default="now")
    s.add_argument("--notes")
    s.add_argument("--id")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_log)

    s = prof(sub.add_parser("metric", help="write one numeric reading (POST /v1/metrics)"))
    s.add_argument("--type", required=True, help=", ".join(sorted(METRIC_TYPES)))
    s.add_argument("--value", type=float, required=True)
    s.add_argument("--unit", help="UCUM, e.g. kg, Cel, mm[Hg], mg/dL")
    s.add_argument("--method", help="blood_glucose: blood|interstitial; heart_rate_variability: sdnn|rmssd")
    s.add_argument("--time", default="now")
    s.add_argument("--source", default=os.environ.get("GUAVA_SOURCE", "guavahealth.com"),
                   help="reverse-DNS or domain of where the reading came from")
    s.add_argument("--id")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_metric)

    s = prof(sub.add_parser("write-raw", help="POST a JSON body to a write endpoint"))
    s.add_argument("--path", required=True, help="/v1/data-entries, /v1/metrics, /v1/sleep, /v1/nutrition, /v1/water, /v1/activities")
    s.add_argument("--body", default="-", help="JSON file, or - for stdin")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_write_raw)

    s = prof(sub.add_parser("search", help="read metrics/sleep/activities/nutrition/water"))
    s.add_argument("resource")
    s.add_argument("--types", help="metrics only: comma-separated types")
    s.add_argument("--start")
    s.add_argument("--end")
    s.add_argument("--count", type=int, default=200)
    s.add_argument("--all", action="store_true", help="follow next links")
    s.add_argument("--max-pages", type=int, default=20)
    s.set_defaults(fn=cmd_search)

    s = prof(sub.add_parser("fhir", help="read a FHIR R4 resource"))
    s.add_argument("resource", help=", ".join(sorted(FHIR_RESOURCES)))
    s.add_argument("--id")
    s.set_defaults(fn=cmd_fhir)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
