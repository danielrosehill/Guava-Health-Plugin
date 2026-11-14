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
- The web app shows one profile at a time. Check the name at the top right before changing anything.
- Saving changes a health record. Show the person the exact change first, unless they gave the exact
  text and the medication in their request.

## Profiles (dependents), V 2026-11-14

- Profile menu: the name button at top right → the chevron **show all profiles or add a profile** →
  one link per profile, plus **Add profile**. The account holder's link is `/today`; a dependent's
  is `/today/p/<profile-id>`.
- The `/p/<profile-id>` suffix works on other pages too: `/profile/p/<profile-id>` opened the
  dependent's Profile page directly (tested). Pages without it (`/sources/...`, `/nfc-settings`) act
  on whichever profile was last selected, so switch first and check the name at top right.
- The profile id is not the API's patient id. Keep it in your own private notes, never in this repo.
- Same menu: **Data sources**, **Reminders**, **Emergency Card**, **Guava Tags**, **Family plan**,
  **Settings**.

## Routes, V 2026-11-14

| Route | What | Skill |
|---|---|---|
| `/today` | Home: today's reminders (Skip / Log), quick add (Add Entry, Meds, Body Temp…), Meds Taken grid | |
| `/profile` | Basic info, biomarkers, Meds & Supplements, Conditions & Injuries, Allergies, Vaccinations, Events, Care Providers, Lifestyle; every edit is a dialog on this page | `manage-medications`, `medication-reminders`, `manage-conditions`, `add-medication-note`, `create-medication-group` |
| `/sources`, `/sources/app`, `/sources/app/add`, `/sources/provider` | Connected sources and the connect tiles | `connect-data-source` |
| `/sources/upload-files` | Document upload (PDF, images, DICOM, CCDA) | `upload-health-files` |
| `/sources/import` | Bulk CSV import, 20 types + Medisafe/Bearable/Visible | `import-csv` |
| `/nfc-settings` | Guava Tags | `manage-guava-tags` |

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
| Profile page Meds & Supplements | `/profile`: Active/Past, Search, **New Med**, **Reminders**, rows open the same details view | V 2026-11-14 |
| Details view, more | **Pills left** → **Set**; **Reminders** with existing rows and **+ New**; **Log Med** | V 2026-11-14 |
| Update Reminder form | from a reminder row; fields in skill `medication-reminders` | V 2026-11-14 (read) |
| Schedule picker | Frequency: Daily, Every X Days, Weekly, Monthly, Cycle | V 2026-11-14 |
| Reminders list | **Reminders** button: week strip, due reminders with Skip/Log, **New Reminder** | V 2026-11-14 |
| New Medication form | **New Med**; fields in skill `manage-medications` | V 2026-11-14 (read) |
| Add Condition form | fields in skill `manage-conditions` | V 2026-11-14 (read) |
| Add Injury, Add Allergy forms | | U |
| Upload page, hidden file-input | `/sources/upload-files` | V 2026-11-14 (read) |
| Import page, Med Usage columns | `/sources/import` | V 2026-11-14 (read) |
| Guava Tags list, tag details, Edit Tag | `/nfc-settings` | V 2026-11-14 (read) |
| Saving a note with **Update** | | U |
| Saving a reminder, a new medication, a condition, a tag; Skip/Log; uploads; imports | | U |
| Confirming the picker, and saving a group | No save control was visible before a medication was chosen | U |

## Read-only views the API lacks

The details view shows last taken, reminders and per-day entries, which the API can't return. An
agent can read them there, one medication at a time, as a last resort.
