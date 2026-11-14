---
name: manage-medications
description: 'Add, edit, stop or end a medication, set pills left, in Guava''s web app using the browser, because the API can''t create (except by logging a dose), edit or stop medications. Fields: name, dosage & timing, prescriber, photo, start/end date, "no longer taking", notes. Use on "add a new medication properly", "change the dose to 40mg", "I stopped taking X", "set pills left", "move X to past meds".'
license: MIT
compatibility: Claude Code with a browser tool (Claude in Chrome or similar) and the user signed in to guavahealth.com.
---

# Manage medications (web)

Browser only for these: the API's only way to create a medication is logging a dose under a new
name, with no dose, schedule or prescriber (docs/api-notes.md, "Gaps"). Read `docs/web-app.md` first.
**Adding, updating and setting pills left haven't been saved by an agent yet (U).**

## Map, V 2026-11-14 (read, not saved)

- `/profile` (dependent: `/profile/p/<profile-id>`) → **Meds & Supplements**: **Active** / **Past**
  tabs, **Search**, **New Med**, **Reminders**, one row per medication.
- **New Med** → New Medication: **Photo**, *Medication or Supplement Name*, *Dosage & Timing*
  ("125 mcg daily with breakfast"), *Prescriber*, *Start Date* (DD/MM/YYYY), **Add End Date**,
  checkbox *I'm no longer taking this*, **Add Notes**, **Add**.
- A row → details: **edit** (same fields, plus **Delete** and **Update**), **Pills left** → **Set**,
  Reminders (skill `medication-reminders`), a calendar of logged doses, **Log Med**.

## Steps

1. Get the medication and exactly what changes. For a new one: name as the user says it (don't
   normalise brand to generic), dosage & timing text, prescriber and start date if given.
2. Open the right profile and check the name at top right.
3. New: **New Med**, fill, then show the user and wait for a yes unless they gave every field; **Add**.
   Edit: open the row → **edit** → change only what was asked → **Update**.
   Stopped: **edit** → *I'm no longer taking this* (and an end date if given) → **Update**. It moves
   to **Past**. Never **Delete** unless asked, and confirm first: delete loses the dose history.
   Pills left: details → **Set**.
4. Reopen and confirm. Afterwards `guava meds` (API) should show the change, since it reads
   `MedicationRequest`. Report what you saw.

Notes on a medication: skill `add-medication-note`.
