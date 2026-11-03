# Guava-Health-Plugin: notes for agents

Public plugin `guava-health`. Unofficial client for the Guava Health API.

## Hard rules

1. **No personal data in this repo.** Never commit client ids, secrets, tokens, profile
   ids, patient ids, names of real family members, medication names from a real account,
   or API responses. Tokens live in `$GUAVA_HOME` (default `~/.config/guava-health`, 0600).
   Use generic examples ("my son", "child", "Paracetamol").
2. **Facts with dates.** The API is young and changing. Every statement about endpoints,
   scopes or the form carries the date it was observed. "Confirmed" means in Guava's docs;
   "tested" means a real call succeeded. Mark which.
3. **The form map is data.** `reference/app-form.json` is the single source for form
   labels, scopes and presets. `docs/creating-the-api-app.md` is its human version, and
   `reference/scopes-full.txt` is the `family-manager` preset. Change all three together.
4. **Writes only on a clear instruction.** There is no API undo. Use `--dry-run` when any
   field was inferred, and `--id` for retries.

## Layout

- `scripts/guava.py`: stdlib CLI (auth with PAR+PKCE, rotating refresh, per-profile tokens, reads, writes). JSON out.
- `skills/*/SKILL.md`: create-api-app, connect-profile, log-medication, log-health-entry, review-health-data.
- `docs/`: api-notes (endpoint reference), family-and-dependents, creating-the-api-app.
- `reference/`: app-form.json, scopes-full.txt.

## State (2026-11-03)

- Built from the signed-in docs page and the New App form. Sandbox PAR tested 2026-11-03
  (see docs/api-notes.md "Tested"). The token exchange and data calls are not tested yet.
- Open questions are listed in `docs/family-and-dependents.md` ("Unverified").
  Resolve them on the first real grant and date the answer.
- Prior art checked 2026-11-03: no Guava MCP server or agent plugin found.
  `bkammerling/guava-auto-log` is a small med-supply auto-log web app.
