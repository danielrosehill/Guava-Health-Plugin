# Guava web app: what only it can do

Observed 2026-11-07, signed in on desktop Chrome. The app is young and may change.

The API can't write medication notes, edit a medication or manage groups (see
[api-notes.md](api-notes.md), "Gaps"), so those need the web app. Use the browser only for these:
if the API or the CLI can do something, use that instead.

Status: **V 2026-11-07** means an agent ran the step on a live account. **U** means it hasn't been run.

## Rules for driving it

- Target elements by reference from a fresh `find` or `read_page`. Never use coordinates: many
  buttons have no name, and refs change whenever a dialog opens.
- The person must already be signed in. Never enter credentials.
- The web app shows the signed-in profile. Check the name at the top right before changing anything.
  Switching to a dependent's profile hasn't been mapped.
- Saving changes a health record. Show the person the exact change first, unless they gave the exact
  text and the medication in their request.

## Map

| Where | How to reach it | Status |
|---|---|---|
| Home | `https://guavahealth.com/today` (`/app` is a 404) | V 2026-11-07 |
| Meds & Supplements dialog | On Home, the **All** button in the medications block. Home has several **All** buttons, and the one after **Took Meds** opens Tracked Symptoms, so check the dialog title reads "Meds & Supplements" | V 2026-11-07 |
| Medication details | A row in that dialog, a button named after the medication. Shows last taken, pills left, reminders, a calendar and dated entries | V 2026-11-07 |
| Edit Medication form | **edit** on the details view. Fields: taking it Yes/No, name, Dosage & Timing, Prescriber, photos, start date, **Add End Date**, **Add Notes**, **Delete**, **Update** | V 2026-11-07 |
| Notes box | **Add Notes** on the form reveals a `Notes` textbox | V 2026-11-07 |
| New Med Group form | **add new med group** in the filter row of the dialog. Fields: Short Group Name, **Select Meds** | V 2026-11-07 |
| Med picker | **Select Meds**. Search box and one option per medication | V 2026-11-07 |
| Saving a note with **Update** | | U |
| Confirming the picker, and saving a group | No save control was visible before a medication was chosen | U |

## Read-only views the API lacks

The details view shows last taken, reminders and per-day entries, which the API can't return. An
agent can read them there, one medication at a time, as a last resort.
