#!/usr/bin/env python3
"""guava-nfc: make your own Guava Tags (unofficial; not made by Guava Health, Inc.): write https://guavahealth.com/nfc/<id> to blank NFC tags.

A Guava Tag holds no health data. It is a URL with a unique id, plus an Android
Application Record so Android opens the Guava app. Tapping a new id opens Guava's
"Let's set up your Guava Tag" dialog. There you pick the profile (yourself or a
dependent) and what the tag logs. The binding lives in the Guava account and can
be edited later, so the tag itself never needs rewriting. See docs/nfc-tags.md.

Commands (JSON on stdout):
  new-id   [--count N] [--label TEXT]   generate unused ids and record them locally
  ndef     --id ID [--no-aar] [--out F] build the NDEF message (hex + optional .ndef file)
  write    --id ID [--no-aar] [--lock]  write to an NTAG21x on a PC/SC reader (ACR122U, ACR1252...)
  read                                  read the tag on the reader and decode its URL
  list                                  ids recorded locally

The write and read commands need pyscard and a running pcscd service:
  uv tool install 'guava-cli[nfc] @ git+https://github.com/danielrosehill/Guava-Health-Plugin'
Without a PC/SC reader, use `ndef --out tag.ndef` and any NDEF writer: a phone app
(add a URL record, then an "Application" record com.guavahealth.app) or another CLI.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import secrets
import string
import sys
import time
from pathlib import Path

URL_BASE = "https://guavahealth.com/nfc/"
AAR_PACKAGE = "com.guavahealth.app"
ID_ALPHABET = string.ascii_letters + string.digits
ID_LEN = 12  # matches the ids on Guava's own tags (observed, 2026-11-03)


def out(o) -> None:
    print(json.dumps(o, indent=2, ensure_ascii=False))


def die(msg: str, **kw) -> None:
    print(json.dumps({"error": msg, **kw}), file=sys.stderr)
    sys.exit(1)


def registry_path() -> Path:
    p = Path(os.environ.get("GUAVA_HOME", Path.home() / ".config" / "guava-health"))
    p.mkdir(parents=True, exist_ok=True)
    return p / "nfc-tags.json"


def registry() -> list[dict]:
    p = registry_path()
    return json.loads(p.read_text()) if p.exists() else []


def save_registry(rows: list[dict]) -> None:
    registry_path().write_text(json.dumps(rows, indent=2, ensure_ascii=False))


def check_id(tag_id: str) -> str:
    if not (6 <= len(tag_id) <= 32 and all(c in ID_ALPHABET for c in tag_id)):
        die("Tag id must be 6-32 letters/digits", got=tag_id)
    return tag_id


# ------------------------------------------------------------------ NDEF

def ndef_message(tag_id: str, aar: bool = True) -> bytes:
    """URI record (+ AAR). URI prefix code 0x04 = 'https://'.

    (Older DIY scripts used 0x02, which is 'https://www.', giving
    https://www.guavahealth.com/... That works only through a redirect.)"""
    uri = (URL_BASE + tag_id)[len("https://"):].encode()
    uri_payload = b"\x04" + uri
    records = [(0x01, b"U", uri_payload)]  # TNF well-known
    if aar:
        records.append((0x04, b"android.com:pkg", AAR_PACKAGE.encode()))  # TNF external
    msg = b""
    for i, (tnf, rtype, payload) in enumerate(records):
        if len(payload) > 255:
            die("payload too long for a short record")
        header = tnf | 0x10  # SR
        if i == 0:
            header |= 0x80  # MB
        if i == len(records) - 1:
            header |= 0x40  # ME
        msg += bytes([header, len(rtype), len(payload)]) + rtype + payload
    return msg


def tlv(msg: bytes) -> bytes:
    if len(msg) < 0xFF:
        return bytes([0x03, len(msg)]) + msg + b"\xFE"
    return bytes([0x03, 0xFF, len(msg) >> 8, len(msg) & 0xFF]) + msg + b"\xFE"


def decode_uri(data: bytes) -> str | None:
    """Pull the first URI record out of NTAG user memory (TLV-wrapped)."""
    try:
        i = data.index(0x03)
    except ValueError:
        return None
    ln = data[i + 1]
    msg = data[i + 2:i + 2 + ln]
    if len(msg) < 4 or msg[1] != 1 or msg[3:4] != b"U":
        return None
    plen = msg[2]
    payload = msg[4:4 + plen]
    prefixes = {0: "", 1: "http://www.", 2: "https://www.", 3: "http://", 4: "https://"}
    return prefixes.get(payload[0], "") + payload[1:].decode(errors="replace")


# ------------------------------------------------------------------ PC/SC

def connect(timeout: int = 30):
    try:
        from smartcard.System import readers
        from smartcard.Exceptions import NoCardException, CardConnectionException
    except ImportError:
        die("pyscard not installed", hint="Install the nfc extra: uv tool install 'guava-cli[nfc] @ git+https://github.com/danielrosehill/Guava-Health-Plugin'")
    rs = readers()
    if not rs:
        die("No PC/SC reader found", hint="Plug in the reader and start pcscd (systemctl start pcscd)")
    reader = next((r for r in rs if "PICC" in str(r)), rs[0])
    print(json.dumps({"reader": str(reader), "status": "place tag on reader"}), file=sys.stderr)
    end = time.time() + timeout
    while time.time() < end:
        try:
            c = reader.createConnection()
            c.connect()
            return c
        except (NoCardException, CardConnectionException):
            time.sleep(0.4)
    die("No tag detected before timeout")


def read_pages(c, start: int, count: int) -> bytes:
    data = b""
    for p in range(start, start + count, 4):  # READ returns 16 bytes = 4 pages
        r, sw1, sw2 = c.transmit([0xFF, 0xB0, 0x00, p, 0x10])
        if sw1 != 0x90:
            die(f"read failed at page {p}", sw=f"{sw1:02X}{sw2:02X}")
        data += bytes(r)
    return data


def cmd_write(a) -> None:
    tag_id = check_id(a.id)
    data = tlv(ndef_message(tag_id, not a.no_aar))
    data += b"\x00" * (-len(data) % 4)
    c = connect(a.timeout)
    cc = read_pages(c, 3, 4)[:4]  # capability container
    if cc[0] != 0xE1:
        die("Tag is not NDEF-formatted (no E1 capability container)", cc=cc.hex())
    capacity = cc[2] * 8
    if len(data) > capacity:
        die("Tag too small", needed=len(data), capacity=capacity)
    if cc[3] & 0x0F:
        die("Tag is write-protected (CC access byte)")
    for n in range(0, len(data), 4):
        page = 4 + n // 4
        r, sw1, sw2 = c.transmit([0xFF, 0xD6, 0x00, page, 0x04] + list(data[n:n + 4]))
        if sw1 != 0x90:
            die(f"write failed at page {page}", sw=f"{sw1:02X}{sw2:02X}")
    back = decode_uri(read_pages(c, 4, max(4, len(data) // 4 + 4)))
    ok = back == URL_BASE + tag_id
    locked = False
    if a.lock and ok:
        # Static lock bits only (pages 3-15). Covers the whole message on NTAG213 for
        # these short URLs. Permanent: the tag can never be rewritten.
        r, sw1, _ = c.transmit([0xFF, 0xB0, 0x00, 0x02, 0x04])
        if sw1 == 0x90:
            _, sw1, _ = c.transmit([0xFF, 0xD6, 0x00, 0x02, 0x04, r[0], r[1], 0xFF, 0xFF])
            locked = sw1 == 0x90
    c.disconnect()
    rows = registry()
    row = next((x for x in rows if x["id"] == tag_id), None)
    if row is None:
        row = {"id": tag_id, "label": a.label}
        rows.append(row)
    row.update({"written_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
                "verified": ok, "locked": locked})
    if a.label:
        row["label"] = a.label
    save_registry(rows)
    out({"ok": ok, "id": tag_id, "url": URL_BASE + tag_id, "read_back": back,
         "bytes": len(data), "capacity": capacity, "locked": locked,
         "next": "Tap the tag with your phone while signed in to Guava, pick the profile and what it logs."})


def cmd_read(a) -> None:
    c = connect(a.timeout)
    url = decode_uri(read_pages(c, 4, 36))
    c.disconnect()
    out({"url": url, "guava_tag": bool(url and url.startswith(URL_BASE)),
         "id": url[len(URL_BASE):] if url and url.startswith(URL_BASE) else None})


def cmd_new_id(a) -> None:
    rows = registry()
    used = {r["id"] for r in rows}
    new = []
    for _ in range(a.count):
        while True:
            i = "".join(secrets.choice(ID_ALPHABET) for _ in range(ID_LEN))
            if i not in used:
                break
        used.add(i)
        rec = {"id": i, "label": a.label, "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds")}
        rows.append(rec)
        new.append({**rec, "url": URL_BASE + i})
    save_registry(rows)
    out(new)


def cmd_ndef(a) -> None:
    tag_id = check_id(a.id)
    m = ndef_message(tag_id, not a.no_aar)
    if a.out:
        Path(a.out).write_bytes(m)
    out({"id": tag_id, "url": URL_BASE + tag_id, "aar": None if a.no_aar else AAR_PACKAGE,
         "ndef_hex": m.hex(), "ntag_tlv_hex": tlv(m).hex(), "bytes": len(m), "file": a.out})


def cmd_list(a) -> None:
    out(registry())


def main() -> None:
    p = argparse.ArgumentParser(prog="guava-nfc", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("new-id"); s.add_argument("--count", type=int, default=1); s.add_argument("--label"); s.set_defaults(fn=cmd_new_id)
    s = sub.add_parser("ndef"); s.add_argument("--id", required=True); s.add_argument("--no-aar", action="store_true"); s.add_argument("--out"); s.set_defaults(fn=cmd_ndef)
    s = sub.add_parser("write"); s.add_argument("--id", required=True); s.add_argument("--label"); s.add_argument("--no-aar", action="store_true")
    s.add_argument("--lock", action="store_true", help="permanently lock after a verified write (not recommended)")
    s.add_argument("--timeout", type=int, default=30); s.set_defaults(fn=cmd_write)
    s = sub.add_parser("read"); s.add_argument("--timeout", type=int, default=30); s.set_defaults(fn=cmd_read)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
