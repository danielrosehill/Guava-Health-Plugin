---
name: review-health-data
description: 'Pull and summarise Guava Health data for the user or a dependent: weight/temperature/BP/heart-rate history, sleep, activities, water, nutrition, and clinical records (medications, allergies, conditions, immunizations, procedures). Use for "how did I sleep this week", "my son''s temperature readings since Sunday", "what meds is he on", "my weight trend", "prep a summary for the doctor".'
license: MIT
compatibility: A connected profile (connect-profile skill). Uses scripts/guava.py.
---

# Review health data

`G="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/guava.py"`.

| Want | Command |
|---|---|
| Metrics | `$G search metrics -p <l> --types weight,height --start 2026-10-01` |
| High-volume metric | one type per call: `--types heart_rate` (also steps, HRV, resting HR, SpO₂, resp rate, glucose, VO₂ max) |
| Sleep | `$G search sleep -p <l> --start <iso> --end <iso>` |
| Activities / water / nutrition | `$G search activities …`, `search water …`, `search nutrition …` |
| Full history | add `--all --count 1000` (metrics up to 10000). Pages via next links, capped by `--max-pages` |
| Medications (prescribed) | `$G fhir MedicationRequest -p <l>` |
| Allergies / conditions / immunizations / procedures / providers | `$G fhir AllergyIntolerance …`, `Condition`, `Immunization`, `Procedure`, `Practitioner` |

Notes:
- Clinical records come from connected patient portals, which Guava supports in the US
  only. Elsewhere they may be empty, or hold only uploaded documents.
- Every entry has a `source`. Mention it when summarising, so device data, in-app logs and
  EHR data aren't mixed up.
- Self-logged entries (doses, symptoms, mood, journal) **can't be read through the API
  yet** (2026-11-03). Say so rather than reporting "none found".
- Keep output lean: pull the window asked for and summarise (min/max/latest, trend),
  rather than dumping raw JSON into the conversation.
