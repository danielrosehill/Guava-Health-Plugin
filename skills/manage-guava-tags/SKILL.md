---
name: manage-guava-tags
description: 'See, change or remove Guava Tags (NFC tags that log a dose when tapped) in the web app: which medications and quantities a tag logs, last tap, tag history. Use on "what does my evening tag log", "add Paracetamol to the evening tag", "remove that tag", "which tags have I got". Writing a physical tag is write-nfc-tag.'
license: MIT
compatibility: Claude Code with a browser tool (Claude in Chrome or similar) and the user signed in to guavahealth.com.
---

# Manage Guava Tags (web)

Read `docs/web-app.md` and `docs/nfc-tags.md` first. **Updating and removing a tag haven't been run by
an agent yet (U).**

## Map, V 2026-11-14 (read, not saved)

- `/nfc-settings` (also profile menu → **Guava Tags**): one row per tag, "Med Usage: <med>[, N
  more]", "Last tap: …"; **Order Tags**; **Help**.
- A row → "Guava Tag: Med Usage": **edit**, **Tag History**, **Remove Tag**.
- **edit** → Edit Tag: *Selected Type* (**change**), "When I tap my Guava Tag, log the following:"
  one row per medication with **×**, **-** / quantity / **+**; **Add More Meds**; **Update**.

## Steps

1. Which tag (by what it logs) and what should change.
2. List with `/nfc-settings`; open the row; **edit**.
3. Change only what was asked. Show the user the new contents and wait for a yes. **Update**.
   **Remove Tag** only when asked, after confirming: the physical tag stops working.
4. Reopen and confirm. Report.
