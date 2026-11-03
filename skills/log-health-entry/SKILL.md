---
name: log-health-entry
description: 'Record a self-reported entry or reading in Guava Health for the user or a dependent: symptoms with severity, mood, energy, journal notes, bowel movements, temperature/fever, weight, height, blood pressure, glucose, heart rate, water, food. Use for "log a fever of 38.4 for my son", "note that he vomited twice", "log my weight", "add a journal entry", "BP 128/82".'
license: MIT
compatibility: A connected profile (connect-profile skill). Uses the guava CLI from this repo (uv tool install).
---

# Log a health entry

If the guava MCP tools are connected (through a gateway they appear as e.g. `mcp__gateway__guava__log_medication`; locally as `mcp__guava__…`), call those instead of the CLI: same arguments, same JSON.

Command: `guava` (package `guava-cli` from this repo). If `command -v guava` fails, install it:
`uv tool install 'git+https://github.com/danielrosehill/Guava-Health-Plugin'`
(add the `[nfc]` extra for tag writing). Prefix calls with the secrets wrapper if credentials live there.

## Whose data

Pass the person's name the way the user said it: `--profile Sam`, `--profile "my son"`
(MCP `profile`). The CLI matches it against each grant's label, friendly name, aliases and
Guava first name. For the account holder ("I", "me", "my"), leave `--profile` out: it
resolves to the grant marked `self`, or to the only grant. If nothing matches or several
match, the error lists the connected profiles. Ask the user rather than guessing, then
offer to save the name they used as an alias (`guava label -p <label> --alias "<name>"`).
Check with `guava resolve -p "<name>"` before any write you aren't sure about. Every
`--dry-run` shows the `profile` it resolved to.

Fields and units: `guava schema` (JSON). Background: `docs/api-notes.md`.

Pick the route by what is being logged:

| What | Command |
|---|---|
| Symptom | `guava log -p <l> --type symptoms -f symptom_name="Cough" -f severity=4` |
| Mood (1–5) | `guava log -p <l> --type mood -f value=3 -f tags=Anxious,Tired` |
| Energy (1–5) | `guava log -p <l> --type energy -f value=2` |
| Journal | `guava log -p <l> --type journal --notes "…"` |
| Bowel movement | `guava log -p <l> --type bowel_movement -f bristol_type=4` |
| Temperature | `guava metric -p <l> --type body_temperature --value 38.4 --unit Cel` |
| Weight / height | `guava metric -p <l> --type weight --value 12.3 --unit kg` |
| Blood pressure | two calls: `systolic_blood_pressure` and `diastolic_blood_pressure`, unit `mm[Hg]`, same `--time` |
| Glucose | `guava metric -p <l> --type blood_glucose --value 5.4 --unit mmol/L --method blood` |
| Water | `guava water -p <l> --ml 250 [--time …]` (MCP `log_water`). Other units: `write-raw --path /v1/water` with `volume.code` `[foz_us]` |
| Food | `guava write-raw -p <l> --path /v1/nutrition`, entries with `time`, `name` and optional nutrients |

Rules:
- Symptoms match by exact name and auto-create on a new name, so reuse existing names.
- Always pass `--time` (local ISO) when the user gave one, and `--id` for anything that might be retried.
- Use `--notes` for context the user gives ("after the vaccine", "before food").
- `sexual_activity` is refused for under-18 profiles. Never log it for a dependent child.
- Report `accepted` and `environment`. Corrections and deletions happen in the Guava app (no API for them).
