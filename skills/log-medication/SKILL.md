---
name: log-medication
description: 'Log a medication dose to Guava Health for the user or a dependent (med_usage), e.g. "gave my son 5 ml paracetamol at 8", "log my Lexapro", "I took 2 ibuprofen an hour ago". Also lists the profile's medications (app-entered and clinical), and handles requests to add, edit or delete a medication (the API can only create one by logging a dose; edit and delete go to the Guava app). Use whenever a dose was taken or given, or for "check <name>''s medications", "add a medication", "delete/stop/rename a medication".'
license: MIT
compatibility: A connected profile (connect-profile skill). Uses the guava CLI from this repo (uv tool install).
---

# Log a medication dose

If the guava MCP tools are connected (through a gateway they appear as e.g. `mcp__gateway__guava__log_medication`; locally as `mcp__guava__…`), call those instead of the CLI: same arguments, same JSON.

Command: `guava` (package `guava-cli` from this repo). If `command -v guava` fails, install it:
`uv tool install 'git+https://github.com/danielrosehill/Guava-Health-Plugin'`
(add the `[nfc]` extra for tag writing). Prefix calls with the secrets wrapper if credentials live there.

1. **Whose dose.** Pass the person as the user said it: `--profile Sam`, `--profile "my son"`.
   It matches each grant's label, friendly name, aliases or Guava first name. For "I/me",
   leave `--profile` out (resolves to the grant marked `self`, or the only grant). If it
   doesn't resolve, the error lists the connected profiles. Ask, don't guess.
2. **Name.** `med_usage` matches by exact name and creates a new medication when the name
   differs. Reuse the name already in the profile: list them with
   `guava fhir MedicationRequest --profile <name>` (`medicationCodeableConcept.text`) and
   match the user's word to one of them. Ask if none fits. Don't normalise brand names to generics.
3. **Quantity** is a plain number of the medication's unit as set up in Guava (tablets,
   ml…), 0.001–1000, default 1. Put the dose description in `--notes` if the unit is unclear.
4. **Time.** Convert "an hour ago" or "at 8" to local ISO time. Default is now.
5. Write it:
   `guava log-med --profile <name> --name "<medication>" --quantity <n> --time <iso> --id <label>-<medication>-<iso>`
   The `--id` makes a retry harmless. Use `--dry-run` first if anything was inferred; it
   shows the `profile` the name resolved to.
6. Confirm from the response: `accepted: 1` means logged. `accepted: 0` means a duplicate
   id. Check `environment` too (live vs test).

## Checking, adding, editing, deleting medications

Probed against live and sandbox on 2026-11-03. Every medication-management path returns
404 (`/v1/medications`, `/v1/medications/_search`, `/v1/medications/{id}`,
`/v1/data-entries/_search`, `/v1/data-entries/{id}`, FHIR `MedicationStatement`), and
`/v1/data-entries` allows POST only (PUT, PATCH and DELETE get 405). So:

| Request | What to do |
|---|---|
| "Check X's medications" | `guava fhir MedicationRequest -p X`. Returns the profile's medication list, **including medications added by hand in the app** (tested live 2026-11-03: `requester` and `reportedReference` are the patient, `intent: plan`, dose in `dosageInstruction[].text`, extra text in `note`), plus any from connected clinical records. Logged doses (history) **cannot be read**. Say so if asked. |
| "Add a medication" | Only by logging a dose under the new exact name (step 5); that creates it. There is no way to set dose, unit or schedule. Confirm first, because it writes a dose entry too. Otherwise send the user to the app. |
| "Edit / rename / change schedule" | Not possible through the API. Guava app. |
| "Delete a medication or a dose" | Not possible through the API. Guava app (entries written by the API are editable and deletable there). |

Re-probe when Guava's docs change, and record the result with its date in `docs/api-notes.md`.
