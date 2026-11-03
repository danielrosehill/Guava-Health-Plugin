# Guava Health Plugin

Unofficial agent plugin (Claude Code skills plus a stdlib Python CLI) for the
[Guava Health](https://guavahealth.com) API.

> **Unofficial.** This is not an official Guava app. It was not developed, reviewed or
> endorsed by Guava Health, Inc. A Guava user built it for their own family's use and
> shares it as-is under the MIT licence. "Guava" and "Guava Tags" are Guava Health's
> names, used here only to describe what this works with. For support with Guava itself,
> contact Guava. For problems with this plugin, open an issue here.

**What this is:** a personal, non-commercial, single-user integration. It is not a product,
a service or a multi-tenant app. Each person who uses it creates their own Guava API app
and runs it for their own household. Their keys and tokens stay on their own machines.
The intended setup is a local AI agent (Claude Code here) calling the Guava API for you,
directly or through a self-hosted MCP/AI gateway on a home server.

What it lets your agent do:

- log medication doses, symptoms, mood, energy, journal notes and bowel movements;
- log readings such as temperature, weight, height, blood pressure, glucose, water and food;
- read metrics, sleep, activities, water, nutrition and FHIR clinical records
  (medications, allergies, conditions, immunizations, procedures);
- do all of this **for dependents on a family plan** (e.g. a parent logging a child's
  doses), with one grant per profile;
- **fill in Guava's "New API App" form for you**, with the scope boxes for a chosen preset.

**Side feature: DIY Guava Tags.** The `write-nfc-tag` skill writes Guava's tag URL onto blank
NFC stickers, so a tap with your phone logs a medication, a group or water in the Guava
app. It doesn't use the API. It's included because it pairs well with the logging. Details:
[docs/nfc-tags.md](docs/nfc-tags.md).

## Family plans in one paragraph

Guava has no family scope. You create one API app, then authorise it once for yourself
and once per dependent, picking the dependent on Guava's consent screen. The plugin keeps
a token per profile under a label (`me`, `child`, …). Details, the scope table for a
child, and what the API can't do yet: [docs/family-and-dependents.md](docs/family-and-dependents.md).

## Setup

The `setup` skill walks through everything below, plus the optional MCP server.


1. Join the API platform at https://guavahealth.com/api, then create an app at
   https://guavahealth.com/api-portal/apps. Field-by-field guide:
   [docs/creating-the-api-app.md](docs/creating-the-api-app.md). Machine-readable form
   map and presets: [reference/app-form.json](reference/app-form.json). Or ask the agent:
   "create my Guava API app" (skill `create-api-app`).
2. Install the CLI (uv, Python 3.9+):
   ```
   uv tool install 'git+https://github.com/danielrosehill/Guava-Health-Plugin'
   # with NFC tag writing on a USB reader:
   uv tool install 'guava-cli[nfc] @ git+https://github.com/danielrosehill/Guava-Health-Plugin'
   ```
   This installs `guava` and `guava-nfc`. `guava schema` prints every entry type, field and unit as JSON.
3. Export the credentials the portal gives you:
   ```
   GUAVA_CLIENT_ID=…  GUAVA_CLIENT_SECRET=…
   # optional: GUAVA_REDIRECT_URI (default https://localhost:8765/callback),
   #           GUAVA_ENV=test (sandbox), GUAVA_HOME (default ~/.config/guava-health)
   ```
4. Connect each profile:
   ```
   guava auth --profile me
   guava auth --profile child   # choose the child on the consent screen
   ```
5. Use it:
   ```
   guava log-med -p child --name "Paracetamol" --quantity 5 --time 2026-11-03T08:00
   guava metric  -p child --type body_temperature --value 38.4 --unit Cel
   guava search metrics -p me --types weight --start 2026-10-01
   guava fhir MedicationRequest -p me
   ```
   Every write takes `--dry-run` and `--id` (idempotency key).

   If you're signing in on a phone or another machine, use `auth -p child --start`, open the
   printed URL anywhere, then run `auth -p child --finish '<the URL you landed on>'`.

## Skills

| Skill | For |
|---|---|
| `setup` | Whole setup: CLI, API app, credentials, profiles, then optionally an MCP server (local or behind a gateway) |
| `create-api-app` | Fill in the API app form in your signed-in browser (stops before Create) |
| `connect-profile` | Authorise yourself or a dependent; list connected profiles |
| `log-medication` | Record a dose (`med_usage`) |
| `log-health-entry` | Symptoms, mood, energy, journal, temperature, weight, BP, glucose, water, food |
| `review-health-data` | Pull and summarise metrics, sleep, activity, clinical records |
| `write-nfc-tag` | *(side feature)* Make DIY Guava Tags on blank NFC stickers and set them up for you or a dependent |

## MCP server (optional)

`guava-mcp` serves the same functions as MCP tools. Run it where the tokens live, e.g. a home
server behind your own MCP gateway, so every client shares one set of grants. Guava rotates
refresh tokens, so a grant can't live on two machines. See [docs/mcp-server.md](docs/mcp-server.md);
the `setup` skill does the deployment.

## Limits of the Guava API (2026-11-03)

No reading back self-logged entries (doses, symptoms, mood, journal), no editing or
deleting through the API, no medication management, and only 7 FHIR resources served.
Medical-record retrieval from patient portals is US only. See [docs/api-notes.md](docs/api-notes.md).

## Install

Clone this repo and add it as a local plugin (`/plugin` → add from directory), or install it
from a marketplace that lists `guava-health`.

MIT licence.
