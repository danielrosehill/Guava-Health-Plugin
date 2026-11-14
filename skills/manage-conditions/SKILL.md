---
name: manage-conditions
description: 'Add or update conditions, injuries and allergies on a Guava profile in the web app, using the browser; the API reads these (FHIR Condition, AllergyIntolerance) but can''t write them. Use on "add asthma to my conditions", "record that my son had bronchiolitis", "add a penicillin allergy", "mark that condition as resolved".'
license: MIT
compatibility: Claude Code with a browser tool (Claude in Chrome or similar) and the user signed in to guavahealth.com.
---

# Conditions, injuries, allergies (web)

Read `docs/web-app.md` first. **Saving hasn't been run by an agent yet (U).**

## Map

- `/profile` (dependent: `/profile/p/<profile-id>`) → **Conditions & Injuries**: **Add Condition**,
  **Add Injury**, **Condition List**; existing items as rows.
- **Add Condition**, V 2026-11-14 (read, not saved): *Condition* textbox ("Type II Diabetes"),
  *Onset Date* (DD/MM/YYYY), **Add End Date**, checkbox *I no longer have this condition*,
  **Add Notes**, **Add**.
- **Add Injury**, **Add Allergy** (Allergies & Intolerances section): not opened yet (U). Map
  them with `find` on first use and record the fields in docs/web-app.md.

## Steps

1. Get the condition name, onset date if known, whether it's resolved, any note. Medical terms as the
   user or the document gives them; don't upgrade a symptom into a diagnosis.
2. Open the right profile; check the name at top right.
3. Fill only what was given. Show the user and wait for a yes unless they gave every field. **Add**.
4. Confirm the row appears; `guava fhir Condition` / `AllergyIntolerance` should return it. Report.
