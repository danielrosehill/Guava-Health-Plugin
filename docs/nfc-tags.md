# DIY Guava Tags (NFC)

Guava sells NFC "Guava Tags" (10 for $19 at https://guavahealth.com/guava-tags). You can
also write your own onto blank NFC stickers. This page covers that.

## Format

Two NDEF records, unlocked:

1. **URI record:** `https://guavahealth.com/nfc/<id>`, with a unique `<id>` per tag.
2. **Android Application Record (AAR):** `com.guavahealth.app`, so Android opens the
   Guava app instead of the browser. iPhones ignore it. Leaving the tag unlocked means
   you can strip the AAR later if you need to.

Encoded with URI prefix code `0x04` (`https://`) this is 74 bytes, which fits NTAG213 (144
bytes) and anything bigger. Some older DIY scripts used prefix `0x02`, which is
`https://www.` and only works through a redirect.

## How the id works (tested 2026-11-03)

- The id is the **tag's own identity**, not a medication id. A freshly generated random
  12-character `[A-Za-z0-9]` id, opened while signed in, brought up Guava's
  **"Let's set up your Guava Tag"** dialog, with a **Profile** picker that lists the
  account holder **and dependents** on a family plan.
- So one tag belongs to one id, and what it logs (a medication, a group, water, a symptom…)
  and for whom is set on first tap and stored in the Guava account. Per Guava's tag
  instructions you can change it later (menu → Guava Tags → select → Edit), so a tag never
  needs rewriting.
- Ids from Guava's own tags are also 12 characters. `guava-nfc new-id` produces the same shape.
- Not tested: whether Guava rejects ids of other lengths, and what happens if two people
  write the same id. Random 12-character ids make collisions negligible.

## Hardware

- **Tags:** NTAG213, 215 or 216 stickers or cards (NDEF-formatted, which is the default).
  For pill bottles that go through a dishwasher, pick waterproof or epoxy tags.
- **Writers:**
  - A USB PC/SC reader (ACS ACR122U, ACR1252U…) plus `pcscd`. `guava-nfc write`
    drives it directly.
  - Or a phone. Use an NFC writer app (e.g. NFC Tools): add a URL record with the tag URL,
    add an "Application" record `com.guavahealth.app`, then write.
  - Or any other NDEF CLI. `guava-nfc ndef --out tag.ndef` gives the raw NDEF message,
    and `ntag_tlv_hex` is the TLV-wrapped form for raw page writes starting at page 4.

## Without a USB reader

`guava-nfc sheet` turns registry ids into a sheet (Markdown, HTML, text or JSON) with each tag
URL, its label and whose it is, plus the phone steps. The `email-nfc-tag-sheet` skill mails it
to the user so they can write the stickers with NFC Tools on Android. The binding can be set up
before writing by opening the URL in a signed-in browser.

## Phones

Guava's tag page says: iPhone XS or newer (iOS 14+), Android 5.0+ with NFC. On Android you
may need to turn on NFC tag reading. The tap spot is near the top on iPhones and often the
middle on Android.

## Ideas

A tag per medication bottle. One tag for a whole daily-meds group, so changing the group in
Guava changes what the tag logs without rewriting it. Separate tags for a half dose and a
full dose. A tag on the child's medicine shelf assigned to the child's profile.
