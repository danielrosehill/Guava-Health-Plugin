---
name: log-medication
description: 'Log a medication dose to Guava Health for the user or a dependent (med_usage), e.g. "gave my son 5 ml paracetamol at 8", "log my Lexapro", "I took 2 ibuprofen an hour ago". Also lists prescribed medications from clinical records. Use whenever a dose was taken or given and should be recorded in Guava.'
license: MIT
compatibility: A connected profile (connect-profile skill). Uses scripts/guava.py.
---

# Log a medication dose

`G="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/guava.py"`, prefixed with the secrets
wrapper if needed.

1. **Whose dose.** Map the person to a label from `$G profiles`. "I/me" is the holder,
   and a named child is their label. If it's ambiguous, ask.
2. **Name.** `med_usage` matches by exact name and creates a new medication when the name
   differs. Reuse the name already in the profile. If unsure, check
   `$G fhir MedicationRequest --profile <label>` (prescribed meds only) or ask the user how
   it appears in their Guava app. Don't normalise brand names to generics.
3. **Quantity** is a plain number of the medication's unit as set up in Guava (tablets,
   ml…), 0.001–1000, default 1. Put the dose description in `--notes` if the unit is unclear.
4. **Time.** Convert "an hour ago" or "at 8" to local ISO time. Default is now.
5. Write it:
   `$G log-med --profile <label> --name "<name>" --quantity <n> --time <iso> --id <label>-<name>-<iso>`
   The `--id` makes a retry harmless. Use `--dry-run` first if anything was inferred.
6. Confirm from the response: `accepted: 1` means logged. `accepted: 0` means a duplicate
   id. Check `environment` too (live vs test).

Cannot do (API, 2026-11-03): read back past doses, edit or delete a dose, or change a
medication's schedule. Send the user to the Guava app for those.
