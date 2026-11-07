---
name: create-medication-group
description: 'Create a medication group in Guava''s web app, such as "Morning meds", using the browser, because the API has no group support. Use on "create a med group" or "group my medications". Groups can also be chosen for a Guava Tag.'
license: MIT
compatibility: Claude Code with a browser tool (Claude in Chrome or similar) and the user signed in to guavahealth.com.
---

# Create a medication group

Browser only because the API has no group endpoints. Read `docs/web-app.md` first: it has the map, the
rules and each step's status. **Confirming the picker and saving the group haven't been run yet (U), so
look at the page at those steps instead of assuming, and report what actually happened.**

## Steps

1. Get the group name and its medications. Run `guava meds` to match the names.
2. Open `https://guavahealth.com/today`. If it asks for sign-in, stop: the user signs in themselves.
3. Check the profile name at the top right is the right person. If not, stop and tell the user.
4. Open the medications block's **All** button, and check the dialog reads "Meds & Supplements".
5. In the filter row, select **add new med group**. Check an existing group doesn't already cover this.
6. Enter the name in **Short Group Name**. Keep it short, like "Morning".
7. Select **Select Meds**. For each medication, search in **Search or Enter Med Name** and choose its
   option. Don't press Enter on text that matches nothing: this box also accepts new names, which
   could create a medication.
8. Close or confirm the picker, using whichever control appears, and check the form lists the meds.
9. Unless the user gave the exact name and medications, show them and wait for a yes.
10. Save with whichever control appears on the form.
11. Reopen the dialog and confirm the group is in the filter row, with the right count.
