---
name: log-health-entry
description: 'Record a self-reported entry or reading in Guava Health for the user or a dependent: symptoms with severity, mood, energy, journal notes, bowel movements, temperature/fever, weight, height, blood pressure, glucose, heart rate, water, food. Use for "log a fever of 38.4 for my son", "note that he vomited twice", "log my weight", "add a journal entry", "BP 128/82".'
license: MIT
compatibility: A connected profile (connect-profile skill). Uses the guava CLI from this repo (uv tool install).
---

# Log a health entry

Command: `guava` (package `guava-cli` from this repo). If `command -v guava` fails, install it:
`uv tool install 'git+https://github.com/danielrosehill/Guava-Health-Plugin'`
(add the `[nfc]` extra for tag writing). Prefix calls with the secrets wrapper if credentials live there.
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
| Water | `guava write-raw -p <l> --path /v1/water` with `{"source":"guavahealth.com","log_type":"manual","entries":[{"time":"…","volume":{"value":250,"code":"mL"}}]}` on stdin |
| Food | `guava write-raw -p <l> --path /v1/nutrition`, entries with `time`, `name` and optional nutrients |

Rules:
- Resolve the person to a label first. Ask if it's ambiguous.
- Symptoms match by exact name and auto-create on a new name, so reuse existing names.
- Always pass `--time` (local ISO) when the user gave one, and `--id` for anything that might be retried.
- Use `--notes` for context the user gives ("after the vaccine", "before food").
- `sexual_activity` is refused for under-18 profiles. Never log it for a dependent child.
- Report `accepted` and `environment`. Corrections and deletions happen in the Guava app (no API for them).
