---
name: upload-health-files
description: 'Upload health documents to a Guava profile in the web app: lab PDFs, visit notes, photos or scans of documents, DICOM imaging, CCDA XML. Guava digitises lab reports. Use on "upload this blood test to Guava", "add my son''s visit summary to Guava", "put the X-ray in Guava".'
license: MIT
compatibility: Claude Code with a browser tool (Claude in Chrome or similar) and the user signed in to guavahealth.com.
---

# Upload health files (web)

Read `docs/web-app.md` first. Uploading sends a medical document to Guava: name the file(s) and
the profile and get a yes before uploading, unless the user named both.

## Map, V 2026-11-14 (a PDF uploaded and saved to a dependent's profile)

- `/sources/upload-files`: "Select a file to upload or drag and drop". Supported: PDF (labs,
  visit notes), photos, document images and videos, DICOM imaging, CCDA (XML).
- A hidden `file-input` sits behind the drop area: `find` "file input" and give its ref to the
  browser's file-upload tool with the local path. Don't click the button (it opens the OS dialog).
- After the upload a **New Document** form opens: *Document Date* (day / month / year), *Document
  Short Name*, *Notes* (optional), **Cancel** / **Save**. Guava reads the file and pre-fills the
  date and name (e.g. "Maccabi - My Vaccinations"); keep them unless empty or a raw file name.
  Digitising (Reading, Classifying, Extracting) carries on after **Save**.
- Saved files are listed under **Recent Documents** on the upload page (status *Extracting* at
  first) and counted under **File Uploads** on `/sources`.
- Several files in one upload appear in one form's Files table, so they become **one** document
  (inferred). Upload one document at a time; only files that belong together (the images of one
  DICOM study) go in together.

## Steps

1. Get the file path(s) and the profile. Switch to that profile **through the menu** (a typed
   `/p/` URL doesn't switch it), then nav **Sources** → **File Uploads**. Check the name at top right:
   the upload goes to whichever profile is active.
2. file-upload to the hidden input (the browser tool takes up to 10 MB per call; local paths only).
3. In **New Document**, check the date and short name, then **Save**.
4. Check that the **File Uploads** count went up and the file is under Recent Documents. Report what
   you saw; digitised results take time to appear under Biomarkers / Records.
