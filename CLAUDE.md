# Guava-Health-Plugin: notes for agents

Public plugin `guava-health`. Unofficial client for the Guava Health API, built by a user. It is
not a Guava product. Keep the "Unofficial" notice at the top of README.md, and never word
anything as if Guava made, endorses or supports it.

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
   `guava_cli/scopes-full.txt` is the `family-manager` preset. Change all three together.
4. **Writes only on a clear instruction.** There is no API undo. Use `--dry-run` when any
   field was inferred, and `--id` for retries.

## Layout

- `guava_cli/`: Python package `guava-cli` (pyproject.toml, hatchling, no core dependencies).
  `uv tool install 'git+https://github.com/danielrosehill/Guava-Health-Plugin'` installs two commands:
  - `guava` (`cli.py`): auth with PAR+PKCE, rotating refresh, per-profile tokens, profile names/relations/aliases (`label`, `resolve`), reads, writes, `schema`, `scopes`, `version`. JSON out.
  - `guava-nfc` (`nfc.py`): DIY Guava Tag writer. The `[nfc]` extra adds pyscard.
  - `guava-mcp` (`mcp_server.py`, extra `[mcp]`, pinned `mcp<2`): thin FastMCP wrapper calling the cli functions. Image: `Dockerfile`.
  - `scopes-full.txt`: the family-manager preset, shipped inside the package.
  Skills call `guava` / `guava-nfc` and install them if missing. Bump `__init__.py`, pyproject and plugin.json versions together.
- `skills/*/SKILL.md`: setup (entry point), create-api-app, connect-profile, log-medication, log-health-entry, review-health-data, export-medications, write-nfc-tag, email-nfc-tag-sheet.
- `docs/`: api-notes (endpoint reference), family-and-dependents, creating-the-api-app, nfc-tags, mcp-server.
- `reference/`: app-form.json.

## State (2026-11-03)

- 0.5.0: `guava meds` (flattened MedicationRequest, csv/md/json export), local dose journal
  `$GUAVA_HOME/dose-log.jsonl` + `guava dose-log` (the API can't read doses), `guava water`
  (untested against the API), `guava-nfc sheet` and `new-id --label … --label … --for`.
  MCP tools `medications`, `dose_log`, `log_water`. Medication notes can't be written.

- 0.4.0: profiles have a friendly name, relation (self | dependent) and aliases in
  `$GUAVA_HOME/profiles.json`; `--profile` resolves any of them and is optional (defaults to
  self). Medication create/edit/delete was probed on live and sandbox: no endpoints exist
  (docs/api-notes.md "Gaps"), so no skill for it beyond log-medication's explanation.

- NFC: a random 12-character id opened Guava's tag setup dialog with a profile picker that includes dependents (tested). Writing to a physical tag with guava-nfc has not been tested yet.

- Built from the signed-in docs page and the New App form. The full sandbox loop was tested
  2026-11-03 (auth, reads, FHIR, writes; see docs/api-notes.md "Tested"). Live is untested:
  test clients only reach a synthetic patient.
- Open questions are listed in `docs/family-and-dependents.md` ("Unverified").
  Resolve them on the first real grant and date the answer.
- Prior art checked 2026-11-03: no Guava MCP server or agent plugin found.
  `bkammerling/guava-auto-log` is a small med-supply auto-log web app.
