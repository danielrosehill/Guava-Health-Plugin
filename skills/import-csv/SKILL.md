---
name: import-csv
description: 'Bulk-import data into Guava from a CSV/TSV in the web app: medication doses (Med Usage) and 20 other types (blood pressure, temperature, weight, sleep, symptoms, mood, labs, allergies, providers…), or a quick import from a Medisafe, Bearable or Visible export. Can build the CSV from another app''s export first. Use on "import my Medisafe history into Guava", "import these temperature readings", "backfill doses from this spreadsheet".'
license: MIT
compatibility: Claude Code with a browser tool (Claude in Chrome or similar) and the user signed in to guavahealth.com.
---

# Import CSV (web)

Prefer the API for a handful of entries (`log-medication`, `log-health-entry`). Use this for bulk
history. Read `docs/web-app.md` first. **No import has been run by an agent yet (U).** Imports write
many records with no API undo: show the user the preview and get a yes.

## Map, V 2026-11-14 (read, not imported)

- `/sources/import` ("Bulk Data Import"): type buttons Activity, Alcohol, Allergy, Blood
  Pressure, Body Temp., Bowel Movement, Energy, Food, Glucose, Journal, Lab Results, Med Usage,
  Mood, Provider, Sexual Activity, Sleep, Symptoms, Water, Weight, Custom Types; quick imports
  **Medisafe**, **Bearable**, **Visible**.
- A type → **Choose File**. .csv / .tsv / .dsv, max 100 MB, header row required. Then a preview where
  you pick columns and units (U).
- **Med Usage** columns: *Date/time Taken*, *Medication Name*, *Quantity* (optional),
  *Timezone* (optional), *Notes* (optional). Guava's example:

  ```csv
  Med Name,Quantity,Taken At
  Tylenol,1,2026-06-28 12:43 AM
  ```

  Use the medication's exact existing name (`guava meds`), or the import creates a new one.
- Imports are listed under **Data Imports** on `/sources`.

## Steps

1. Get the source file and the profile. If converting another app's export, write the CSV to a
   temp dir with the columns above, and show the user the row count, date range and medication names.
2. Open the profile; check the name at top right.
3. `/sources/import` → type → **Choose File** (file-upload to the hidden input via `find`).
4. In the preview, map columns and units; screenshot it for the user; wait for a yes; import.
5. Check **Data Imports** and a few entries in the app. Report counts.
