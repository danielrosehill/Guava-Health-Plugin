"""guava-mcp: thin MCP server over guava_cli (unofficial; not made by Guava Health, Inc.).

Runs where the tokens live (e.g. a home server behind an MCP gateway) so every client
shares one set of grants. Guava rotates refresh tokens on every use, so a grant must
live in exactly one place. Tools mirror the CLI and return its JSON.

Env: GUAVA_CLIENT_ID, GUAVA_CLIENT_SECRET (+ optional GUAVA_TEST_CLIENT_*), GUAVA_HOME
(token dir, mount a volume), GUAVA_REDIRECT_URI, MCP_TRANSPORT (streamable-http | stdio),
MCP_HOST (0.0.0.0), MCP_PORT (3000), MCP_STATELESS (true).
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import types
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from . import __version__
from . import cli

mcp = FastMCP(
    "guava",
    instructions=(
        "Unofficial Guava Health client. Every data tool takes `profile`: a grant's label, "
        "friendly name or alias (see `profiles`; e.g. 'me', a child's first name, 'my son'). "
        "Omit it for the account holder (relation self) or when only one profile is connected. "
        "Use `resolve` to check who a name maps to before writing. Writes are "
        "append-only through the API (no edit/delete); pass `id` to make retries harmless. "
        "Self-logged entries (doses, symptoms, mood) cannot be read back through the API. "
        "Call `schema` for entry types, fields and units."),
    host=os.environ.get("MCP_HOST", "0.0.0.0"),
    port=int(os.environ.get("MCP_PORT", "3000")),
    stateless_http=os.environ.get("MCP_STATELESS", "true").lower() == "true",
    # Behind a gateway the Host header is the container name, which FastMCP's DNS-rebinding
    # protection rejects (421). Off by default for the container; set MCP_DNS_REBINDING=on to keep it.
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=os.environ.get("MCP_DNS_REBINDING", "off") == "on",
        allowed_hosts=["*"], allowed_origins=["*"]),
)


def _run(fn, **kw) -> Any:
    """Call a cli command, capture its JSON stdout; turn die() into a returned error."""
    ns = types.SimpleNamespace(**kw)
    buf_out, buf_err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            fn(ns)
    except SystemExit:
        err = buf_err.getvalue().strip()
        try:
            return json.loads(err.splitlines()[-1])
        except (ValueError, IndexError):
            return {"error": err or "failed"}
    text = buf_out.getvalue().strip()
    try:
        return json.loads(text) if text else {"ok": True}
    except ValueError:
        return {"output": text}


def _snapshot_env():
    # load_token() may switch GUAVA_ENV/credentials per grant; restore after each call
    return {k: os.environ.get(k) for k in ("GUAVA_ENV", "GUAVA_CLIENT_ID", "GUAVA_CLIENT_SECRET")}


def _restore_env(snap):
    for k, v in snap.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


def run(fn, **kw):
    snap = _snapshot_env()
    try:
        return _run(fn, **kw)
    finally:
        _restore_env(snap)


# ---------------------------------------------------------------- grants

@mcp.tool()
def profiles() -> Any:
    """List connected Guava profiles: label, friendly name, relation (self | dependent),
    aliases, Guava profile name, environment, refresh token present."""
    return run(cli.cmd_profiles)


@mcp.tool()
def resolve(profile: str | None = None) -> Any:
    """Which connected profile a label, name or alias refers to (none = the account holder)."""
    return run(cli.cmd_resolve, profile=profile)


@mcp.tool()
def label_profile(profile: str, name: str | None = None, relation: str | None = None,
                  aliases: list[str] | None = None, clear_aliases: bool = False) -> Any:
    """Set a connected profile's friendly name, relation ('self' for the account holder,
    'dependent' for a managed profile such as a child) and extra aliases ('my son')."""
    return run(cli.cmd_label, profile=profile, name=name, relation=relation, alias=aliases,
               clear_aliases=clear_aliases)


@mcp.tool()
def whoami(profile: str | None = None) -> Any:
    """GET /v1/me for a grant: the granting user and the profile it acts on."""
    return run(cli.cmd_me, profile=profile)


@mcp.tool()
def auth_start(profile: str, name: str | None = None, relation: str | None = None,
               aliases: list[str] | None = None, scopes: str | None = None) -> Any:
    """Begin authorising a profile. `profile` is the new short label (e.g. 'me', a child's
    first name in lowercase); `name`, `relation` ('self' | 'dependent') and `aliases` are
    saved with the grant. Returns a consent URL (valid 10 min). The user opens it, signs in
    as the account holder, SELECTS the profile (self or dependent) and approves, then gives
    you the URL they land on for auth_finish."""
    return run(cli.cmd_auth, profile=profile, start=True, finish=None, scopes=scopes,
               name=name, relation=relation, alias=aliases,
               scopes_file=str(cli.DEFAULT_SCOPES_FILE), paste=False, no_browser=True, timeout=0)


@mcp.tool()
def auth_finish(profile: str, redirect_url: str) -> Any:
    """Complete auth_start with the full redirect URL (https://localhost:8765/callback?code=...&state=...)."""
    return run(cli.cmd_auth, profile=profile, start=False, finish=redirect_url, scopes=None,
               scopes_file=str(cli.DEFAULT_SCOPES_FILE), paste=False, no_browser=True, timeout=0)


# ---------------------------------------------------------------- writes

@mcp.tool()
def log_medication(medication_name: str, profile: str | None = None, quantity: float | None = None,
                   time: str = "now", notes: str | None = None, id: str | None = None,
                   dry_run: bool = False) -> Any:
    """Log a medication dose (med_usage). Use the exact name already in the profile; a new
    name creates a new medication. time: ISO 8601 (local time assumed without offset) or 'now'."""
    return run(cli.cmd_log_med, profile=profile, name=medication_name, quantity=quantity,
               time=time, notes=notes, id=id, dry_run=dry_run, json=None)


@mcp.tool()
def log_entry(type: str, profile: str | None = None, entries: list[dict] | None = None,
              fields: dict | None = None, time: str = "now", notes: str | None = None,
              id: str | None = None, dry_run: bool = False) -> Any:
    """Write self-reported data entries: type is one of med_usage, symptoms, mood, energy,
    journal, bowel_movement, menstrual_cycle, sexual_activity. Either pass `entries` (list of
    entry objects, batch) or `fields` for a single entry (e.g. {"symptom_name":"Cough",
    "severity":4}). See `schema`."""
    if entries:
        return run(cli.cmd_log, profile=profile, type=type, json=json.dumps(entries),
                   field=None, time=time, notes=None, id=None, dry_run=dry_run)
    field = [f"{k}={json.dumps(v) if not isinstance(v, str) else v}" if k != "tags"
             else f"tags={','.join(v) if isinstance(v, list) else v}" for k, v in (fields or {}).items()]
    return run(cli.cmd_log, profile=profile, type=type, json=None, field=field, time=time,
               notes=notes, id=id, dry_run=dry_run)


@mcp.tool()
def log_metric(type: str, value: float, profile: str | None = None, unit: str | None = None,
               method: str | None = None, time: str = "now", source: str = "guavahealth.com",
               id: str | None = None, dry_run: bool = False) -> Any:
    """Write one numeric reading (weight, height, body_temperature, systolic_blood_pressure,
    diastolic_blood_pressure, blood_glucose, heart_rate, ...). Units are UCUM (kg, Cel, mm[Hg],
    mmol/L). Blood pressure is two calls with the same time."""
    return run(cli.cmd_metric, profile=profile, type=type, value=value, unit=unit,
               method=method, time=time, source=source, id=id, dry_run=dry_run)


# ---------------------------------------------------------------- reads

@mcp.tool()
def search(resource: str, profile: str | None = None, types: str | None = None, start: str | None = None,
           end: str | None = None, count: int = 200, all_pages: bool = False,
           max_pages: int = 20) -> Any:
    """Read metrics | sleep | activities | nutrition | water. For metrics, `types` is required
    (comma-separated; high-volume types like heart_rate or steps must be alone). Read each
    entry's `unit`; it may differ from what was written."""
    return run(cli.cmd_search, profile=profile, resource=resource, types=types, start=start,
               end=end, count=count, all=all_pages, max_pages=max_pages)


@mcp.tool()
def fhir_read(resource: str, profile: str | None = None, id: str | None = None) -> Any:
    """Read clinical records (FHIR R4): Patient, Practitioner, AllergyIntolerance, Condition,
    Procedure, MedicationRequest, Immunization."""
    return run(cli.cmd_fhir, profile=profile, resource=resource, id=id)


@mcp.tool()
def medications(profile: str | None = None, status: str = "active", source: str = "all",
                format: str = "json") -> Any:
    """The profile's medication list, flattened from FHIR MedicationRequest: name, status, dose
    text, as-needed, start, source ('Guava app' for app-entered, else the clinical record), RxNorm,
    notes. status: active | stopped | completed | all. source: all | app | clinical.
    format: json, or csv / md to get an export as text. Use the exact `name` when logging a dose."""
    return _text_or_json(cli.cmd_meds, format, profile=profile, status=status, source=source)


@mcp.tool()
def dose_log(profile: str | None = None, medication: str | None = None, since: str | None = None,
             until: str | None = None, format: str = "json") -> Any:
    """Doses logged through this server (local journal; the API has no read for doses, so ones
    logged in the Guava app or by tag tap are missing). Filters: profile, medication substring,
    since/until (ISO). format: json, csv or md."""
    return _text_or_json(cli.cmd_dose_log, format, profile=profile, medication=medication,
                         since=since, until=until)


@mcp.tool()
def log_water(ml: float, profile: str | None = None, time: str = "now", id: str | None = None,
              dry_run: bool = False) -> Any:
    """Log water drunk, in millilitres (POST /v1/water)."""
    return run(cli.cmd_water, profile=profile, ml=ml, time=time, source="guavahealth.com",
               id=id, dry_run=dry_run)


def _text_or_json(fn, format, **kw):
    if format not in ("json", "csv", "md"):
        return {"error": "format must be json, csv or md"}
    return run(fn, format=format, out=None, **kw)


@mcp.tool()
def schema(section: str | None = None) -> Any:
    """Entry types, fields, units and API limits: data_entries | metrics | search | fhir."""
    return run(cli.cmd_schema, section=section)


@mcp.tool()
def version() -> Any:
    """guava-cli version, environment and token directory of this server."""
    return run(cli.cmd_version)


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "streamable-http")
    mcp.run(transport="stdio" if transport == "stdio" else "streamable-http")


if __name__ == "__main__":
    main()
