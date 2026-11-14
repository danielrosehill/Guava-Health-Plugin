---
name: upload-health-files
description: 'Upload health documents to a Guava profile in the web app: lab PDFs, visit notes, photos or scans of documents, DICOM imaging, CCDA XML. Guava digitises lab reports. Use on "upload this blood test to Guava", "add my son''s visit summary to Guava", "put the X-ray in Guava".'
license: MIT
compatibility: Claude Code with a browser tool (Claude in Chrome or similar) and the user signed in to guavahealth.com.
---

# Upload health files (web)

Read `docs/web-app.md` first. Uploading sends a medical document to Guava: name the file(s) and
the profile and get a yes before uploading, unless the user named both.

## Map, V 2026-11-14 (read; no upload run yet, U)

- `/sources/upload-files`: "Select a file to upload or drag and drop". Supported: PDF (labs,
  visit notes), photos, document images and videos, DICOM imaging, CCDA (XML).
- A hidden `file-input` sits behind the drop area: `find` "file input" and give its ref to the
  browser's file-upload tool with the local path. Don't click the button (it opens the OS dialog).
- Uploaded files are listed under **File Uploads** on `/sources`.

## Steps

1. Get the file path(s) and the profile. Open that profile (docs/web-app.md, "Profiles") and check
   the name at top right: the upload goes to whichever profile is showing.
2. `/sources/upload-files` → file-upload to the hidden input.
3. Wait, then check **File Uploads** for the file and any processing status. Report what you saw;
   digitised results may take time to appear under Biomarkers / Records.
