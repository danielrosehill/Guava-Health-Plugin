---
name: review-health-data
description: 'Pull and summarise Guava Health data for the user or a dependent: weight/temperature/BP/heart-rate history, sleep, activities, water, nutrition, and clinical records (medications, allergies, conditions, immunizations, procedures). Use for "how did I sleep this week", "my son''s temperature readings since Sunday", "what meds is he on", "my weight trend", "prep a summary for the doctor".'
license: MIT
compatibility: A connected profile (connect-profile skill). Uses the guava CLI from this repo (uv tool install).
---

# Review health data

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

## Commands

| Want | Command |
|---|---|
| Metrics | `guava search metrics -p <l> --types weight,height --start 2026-10-01` |
| High-volume metric | one type per call: `--types heart_rate` (also steps, HRV, resting HR, SpO₂, resp rate, glucose, VO₂ max) |
| Sleep | `guava search sleep -p <l> --start <iso> --end <iso>` |
| Activities / water / nutrition | `guava search activities …`, `search water …`, `search nutrition …` |
| Full history | add `--all --count 1000` (metrics up to 10000). Pages via next links, capped by `--max-pages` |
| Medications (the app list, incl. hand-entered, plus clinical) | `guava meds -p <l> [--status all]` (flattened), or raw `guava fhir MedicationRequest -p <l>`. Export: skill `export-medications` |
| Allergies / conditions / immunizations / procedures / providers | `guava fhir AllergyIntolerance …`, `Condition`, `Immunization`, `Procedure`, `Practitioner` |

Notes:
- Clinical records come from connected patient portals, which Guava supports in the US
  only. Elsewhere they may be empty, or hold only uploaded documents.
- Every entry has a `source`. Mention it when summarising, so device data, in-app logs and
  EHR data aren't mixed up.
- Self-logged entries (doses, symptoms, mood, journal) **can't be read through the API
  yet** (2026-11-03). Say so rather than reporting "none found".
- Keep output lean: pull the window asked for and summarise (min/max/latest, trend),
  rather than dumping raw JSON into the conversation.
