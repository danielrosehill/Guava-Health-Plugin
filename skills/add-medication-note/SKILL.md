---
name: add-medication-note
description: 'Add or change the note on a medication in Guava''s web app, using the browser, because the API can''t write medication notes. Use on "add a note to my medication" or "note on this med". A note on a single dose doesn''t need this: use log-medication or log-health-entry.'
license: MIT
compatibility: Claude Code with a browser tool (Claude in Chrome or similar) and the user signed in to guavahealth.com.
---

# Add a medication note

Browser only because no API route exists (tested 2026-11-03). Read `docs/web-app.md` first: it has the
map, the rules and each step's status. **The final save hasn't been run yet (U), so watch that step
and report what actually happened.**

## Steps

1. Get the medication and the exact note text. Don't guess either.
2. Open `https://guavahealth.com/today`. If it asks for sign-in, stop: the user signs in themselves.
3. Check the profile name at the top right is the right person. If not, stop and tell the user.
4. Open the medications block's **All** button, and check the dialog reads "Meds & Supplements".
5. Find the row named after the medication and open it. Past medications are under the **Past** tab.
6. Select **edit**.
7. If a `Notes` textbox already shows text, keep it unless the user asked to replace it. Otherwise
   select **Add Notes**, then find the `Notes` textbox.
8. Enter the note. Leave every other field alone.
9. Unless the user gave the exact text and medication, show them both and wait for a yes.
10. Select **Update**. Never select **Delete**.
11. Reopen **edit** and confirm the note is there. Report that, rather than assuming it saved.

Afterwards, `guava meds` should show the note, because `MedicationRequest.note` carries it.
