# Guava Health Plugin

Unofficial agent plugin (Claude Code skills plus a stdlib Python CLI) for the
[Guava Health](https://guavahealth.com) API. Not affiliated with Guava Health, Inc.

It lets an agent:

- log medication doses, symptoms, mood, energy, journal notes and bowel movements;
- log readings such as temperature, weight, height, blood pressure, glucose, water and food;
- read metrics, sleep, activities, water, nutrition and FHIR clinical records
  (medications, allergies, conditions, immunizations, procedures);
- do all of this **for dependents on a family plan** (e.g. a parent logging a child's
  doses), with one grant per profile;
- **fill in Guava's "New API App" form for you**, with the scope boxes for a chosen preset.

## Family plans in one paragraph

Guava has no family scope. You create one API app, then authorise it once for yourself
and once per dependent, picking the dependent on Guava's consent screen. The plugin keeps
a token per profile under a label (`me`, `child`, …). Details, the scope table for a
child, and what the API can't do yet: [docs/family-and-dependents.md](docs/family-and-dependents.md).

## Setup

1. Join the API platform at https://guavahealth.com/api, then create an app at
   https://guavahealth.com/api-portal/apps. Field-by-field guide:
   [docs/creating-the-api-app.md](docs/creating-the-api-app.md). Machine-readable form
   map and presets: [reference/app-form.json](reference/app-form.json). Or ask the agent:
   "create my Guava API app" (skill `create-api-app`).
2. Export the credentials the portal gives you:
   ```
   GUAVA_CLIENT_ID=…  GUAVA_CLIENT_SECRET=…
   # optional: GUAVA_REDIRECT_URI (default https://localhost:8765/callback),
   #           GUAVA_ENV=test (sandbox), GUAVA_HOME (default ~/.config/guava-health)
   ```
3. Connect each profile:
   ```
   python3 scripts/guava.py auth --profile me
   python3 scripts/guava.py auth --profile child   # choose the child on the consent screen
   ```
4. Use it:
   ```
   python3 scripts/guava.py log-med -p child --name "Paracetamol" --quantity 5 --time 2026-11-03T08:00
   python3 scripts/guava.py metric  -p child --type body_temperature --value 38.4 --unit Cel
   python3 scripts/guava.py search metrics -p me --types weight --start 2026-10-01
   python3 scripts/guava.py fhir MedicationRequest -p me
   ```
   Every write takes `--dry-run` and `--id` (idempotency key).

## Skills

| Skill | For |
|---|---|
| `create-api-app` | Fill in the API app form in your signed-in browser (stops before Create) |
| `connect-profile` | Authorise yourself or a dependent; list connected profiles |
| `log-medication` | Record a dose (`med_usage`) |
| `log-health-entry` | Symptoms, mood, energy, journal, temperature, weight, BP, glucose, water, food |
| `review-health-data` | Pull and summarise metrics, sleep, activity, clinical records |

## Limits of the Guava API (2026-11-03)

No reading back self-logged entries (doses, symptoms, mood, journal), no editing or
deleting through the API, no medication management, and only 7 FHIR resources served.
Medical-record retrieval from patient portals is US only. See [docs/api-notes.md](docs/api-notes.md).

## Install

Clone this repo and add it as a local plugin (`/plugin` → add from directory), or install it
from a marketplace that lists `guava-health`.

MIT licence.
