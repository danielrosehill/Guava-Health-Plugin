---
name: write-nfc-tag
description: 'Make DIY Guava Tags: generate a tag id, write https://guavahealth.com/nfc/<id> plus the Guava Android app record to a blank NFC sticker (NTAG213/215/216) with a USB reader, a phone app or another NFC CLI, verify it, then set it up in Guava for yourself or a dependent. Use for "write a Guava tag", "make an NFC tag for my meds", "tag for my son''s inhaler", "program NFC stickers for Guava".'
license: MIT
compatibility: Python 3.9+. Writing with a USB PC/SC reader needs pyscard (uv run --with pyscard) and pcscd running. Otherwise any NDEF writer (phone app or CLI). No Guava API credentials needed.
---

# Write a Guava NFC tag

Background and format: `docs/nfc-tags.md`.
Command: `guava-nfc`. If it's missing, install it with the reader extra:
`uv tool install 'guava-cli[nfc] @ git+https://github.com/danielrosehill/Guava-Health-Plugin'`.

1. **What and for whom.** Ask whose tags (yourself or a dependent) and what each one logs.
   For medication tags, offer the profile's list: `guava meds -p <name> --source app` (MCP:
   `medications`), and use the exact Guava name as the label so it matches what the user picks
   in Guava's setup dialog. `--label` and `--for` are local notes only. The real binding (which
   medication, which profile) is set in Guava when the tag is first tapped; the API can't set it.
2. **Ids.** `guava-nfc new-id --for "<person>" --label "<med 1>" --label "<med 2>"` gives one id
   per label (or `--count <n>` with one label). Recorded in `$GUAVA_HOME/nfc-tags.json`. Never
   reuse an id across tags.
3. **Pick the writer** that's available:
   - **PC/SC reader:** check `pcsc_scan` (or `systemctl is-active pcscd`). Then
     `guava-nfc write --id <id> --label "<label>"`. Ask the user to put the
     tag on the reader when stderr says so. Success is `"ok": true` with `read_back` equal to
     the URL. One tag at a time: wait for the user to swap tags between writes.
   - **Another NFC CLI** on the machine: `guava-nfc ndef --id <id> --out /tmp/<id>.ndef` and feed it
     the raw NDEF file, or `ntag_tlv_hex` for page-level writes from page 4.
   - **No reader:** switch to the `email-nfc-tag-sheet` skill, which emails the user every
     URL with the phone-app steps (`guava-nfc sheet`).
4. **Don't lock** unless the user insists and understands it's permanent (`--lock`). Locking
   isn't needed: what the tag logs is changed in Guava, not on the tag.
5. **Verify** with `guava-nfc read` if a reader is present.
6. **Set it up:** the user taps the tag with a phone signed in to Guava, or opens the URL
   in a signed-in browser. "Let's set up your Guava Tag" appears. Choose the **Profile**
   (yourself or a dependent), then what it logs. Rebinding later: Guava menu → Guava Tags → Edit.

Never write ids or labels that reveal someone's medications into a shared repo. The local
registry is the only record.
