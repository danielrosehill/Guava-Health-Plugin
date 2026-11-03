---
name: email-nfc-tag-sheet
description: 'No USB NFC reader? Make DIY Guava Tags with an Android phone instead: generate one tag URL per medication (or group, water, symptom), and email the user a sheet with each URL and the phone steps (NFC Tools: URL record + Application record com.guavahealth.app), so they write the stickers themselves. Use for "I don''t have a reader", "send me the tag links", "email me the NFC tags for my meds", "make tags I can write with my phone".'
license: MIT
compatibility: guava-nfc (from this repo; no reader or pyscard needed). The medication list needs a connected profile (guava CLI or guava MCP tools). Sending needs an email tool in the agent (e.g. a Gmail MCP); otherwise the sheet is saved as a file.
---

# Email a Guava Tag sheet (phone-written tags)

The alternative to `write-nfc-tag` when there is no USB PC/SC reader. Format and background:
`docs/nfc-tags.md`. Commands: `guava-nfc`, `guava` (install: `uv tool install 'git+https://github.com/danielrosehill/Guava-Health-Plugin'`).

1. **Whose and what.** Ask for whom (yourself or a dependent) and what each tag logs. Offer the
   profile's medications as the list to choose from:
   `guava meds -p <name> --source app` (or MCP `medications(profile=…, source="app")`). Use each
   medication's exact Guava name as the label, so the user can pick the same name in Guava's
   setup dialog. Groups ("evening meds"), water or a symptom are fine too.
2. **Ids.** One per sticker, never shared:
   `guava-nfc new-id --for "<person>" --label "<med 1>" --label "<med 2>" …`
   (repeat `--label` for several; `--count` for several identical ones, e.g. a half-dose and a
   full-dose tag get two labels instead). Note the returned ids.
3. **Sheet.** `guava-nfc sheet --id <id> --id <id> --format html --out /tmp/guava-tags.html`
   (also `md` or `text` for a plain-text mail). Leave out `--id` for every id in the registry.
4. **Send it to the user's own address**, with the HTML as the body, subject like
   "Guava Tags to write (3)". Use the email tool the agent has (send to the user, not anyone
   else). Say before sending that the labels name their medications and will leave the
   machine. If there is no mail tool, give the file path and paste the text sheet in chat.
5. **What the user does on the phone** (it's in the sheet): install NFC Tools, add a URL
   record with the tag URL, add an Application record `com.guavahealth.app`, write, don't lock,
   then tap the tag and in "Let's set up your Guava Tag" choose the profile and what it logs.
   The binding can be done before the sticker is written by opening the URL in a signed-in
   browser (tested 2026-11-03: the dialog opens with a profile picker that includes dependents).
6. **Check later** if a reader turns up: `guava-nfc read` decodes a written tag.

iPhone users can write the URL record too (iOS ignores the Application record). The phone app
steps are written from the NFC Tools menus and were not run end to end by this repo (2026-11-03).
