---
name: medication-reminders
description: 'Create, change, pause or delete medication reminders in Guava''s web app, using the browser, because the API has no reminder routes. A reminder can cover several medications (e.g. "evening meds") with a quantity each, on a schedule (daily, every X days, weekly, monthly, cycle) or once. Also Skip/Log on a due reminder. Use on "remind me to take X at 9", "add Y to my evening meds", "change the reminder time", "set a reminder for my son''s iron drops".'
license: MIT
compatibility: Claude Code with a browser tool (Claude in Chrome or similar) and the user signed in to guavahealth.com.
---

# Medication reminders (web)

Browser only: no API route reads or writes reminders (probed 2026-11-03). Read `docs/web-app.md`
first for the rules, profile switching and step status. **Saving a reminder has not been run by an
agent yet (U): watch that step and report what actually happened.**

## Where reminders live

- **One medication's reminders:** `/profile` (or `/profile/p/<profile-id>` for a dependent) →
  Meds & Supplements → the medication's row → details dialog → **Reminders** section: existing
  reminders as rows ("Daily: 08:00 Morning meds"), and **+ New**.
- **All of a profile's reminders:** the **Reminders** button under Meds & Supplements, or profile
  menu → **Reminders**. A week strip, each due reminder with **Skip** / **Log**, and **New Reminder**.
- **Home** (`/today`) shows today's due reminders with **Skip** / **Log**.

## The reminder form (New / Update Reminder), V 2026-11-14 (read, not saved)

| Field | Control |
|---|---|
| Medications to take | one row per medication: **×** remove, **-** / quantity / **+**; **Add More Meds** |
| Recurring / Once | listbox |
| Schedule | button → Frequency: Daily, Every X Days, Weekly, Monthly, Cycle |
| Times | button (e.g. 08:00) |
| Start / End | buttons; End defaults to Never |
| Reminder Name | textbox, optional |
| Note | textbox, optional ("take with food") |
| **Delete** / **Save** | bottom of the form (scroll the dialog) |

## Steps

1. Get: whose reminder, which medications and quantities, the schedule and time(s), start/end,
   name. Don't guess a time or a dose.
2. Open the right profile (docs/web-app.md, "Profiles") and check the name at top right.
3. To change an existing reminder, open it from the medication's details or the Reminders list.
   To add one, use **+ New** on the medication (it starts with that medication) or **New Reminder**.
4. Fill only the fields asked for. Refs change when a picker opens: `find` again after each.
5. Show the user the full reminder (meds × qty, schedule, time, start/end, name) and wait for a
   yes, unless they gave every detail.
6. **Save**. Never **Delete** unless asked, and then confirm first.
7. Reopen the reminder and confirm it reads back as intended. Report that.

**Skip / Log** on a due reminder writes a dose (Log) or a skip: only on a clear instruction. To log
a dose without the browser, prefer `log-medication` (API).
