---
name: export-medications
description: 'Export a Guava Health medication list (name, status, dose, as-needed, start, source, notes) and a medication dose log, for the user or a dependent, as CSV, Markdown or JSON, e.g. for a doctor, a school or a carer. Use for "export my son''s medication list", "medication list for the GP", "export the dose log", "what doses did I log this week", "medication history as a spreadsheet".'
license: MIT
compatibility: A connected profile (connect-profile skill). guava CLI from this repo, or the guava MCP tools (medications, dose_log).
---

# Export medications and doses

Command: `guava` (install: `uv tool install 'git+https://github.com/danielrosehill/Guava-Health-Plugin'`).
If the guava MCP tools are connected, use `medications(...)` and `dose_log(...)` with the same
filters; `format="csv"|"md"` returns the export as text in `output`.

## Medication list

`guava meds -p <name> [--status active|stopped|completed|all] [--source all|app|clinical] --format csv|md|json --out <file>`

From FHIR `MedicationRequest` (tested live 2026-11-03: includes medications entered by hand
in the app, with the dose text and notes typed there). `source` is `Guava app` for those,
otherwise the clinical record it came from. Default is active only; say so in the export.

## Dose log

`guava dose-log [-p <name>] [--medication <text>] [--since <iso>] [--until <iso>] --format csv|md|json --out <file>`

**Limit, say it every time:** Guava's API cannot read logged doses back (probed live and
sandbox 2026-11-03). This log is a local journal of doses written **through this plugin**
(`$GUAVA_HOME/dose-log.jsonl`, on whichever machine or MCP server did the writing, since
0.5.0). Doses logged in the Guava app or by tag tap are not in it. For a complete history,
the user exports from the Guava app itself.

## Steps

1. Resolve whose data (`guava resolve -p <name>`); ask if unclear.
2. Pick the format from the purpose: CSV for a spreadsheet, Markdown for a message or doc,
   JSON for another tool. Name files `YYYY-MM-DD_<person>-medications.<ext>` and
   `…_<person>-dose-log.<ext>`.
3. Run the command(s); report the row count and the file path, plus the dose-log caveat.
4. Deliver where the user asked. Sending it to someone else (a doctor, a school) is their
   call: confirm the recipient before it leaves the machine.

Never put an export into a git repo.
