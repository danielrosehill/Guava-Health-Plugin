---
name: connect-data-source
description: 'Connect a device or app (Garmin, Oura, Withings, Health Connect, Google Fit, Fitbit, Dexcom, Omron…) or a health system to a Guava profile, via the web app. The agent opens the right tile; the user completes the third-party sign-in. Use on "connect my Fitbit to Guava", "link Health Connect", "what sources are connected".'
license: MIT
compatibility: Claude Code with a browser tool (Claude in Chrome or similar) and the user signed in to guavahealth.com.
---

# Connect a data source (web)

Read `docs/web-app.md` first. The third-party sign-in and consent are always the user's: never enter
credentials, never approve an OAuth consent screen for them.

## Map, V 2026-11-14

- `/sources`: left column **Devices & Apps** (*N connected*), **File Uploads**, **Data Imports**,
  **Health Systems**.
- `/sources/app`: connected sources. `/sources/app/add`: "Tap to connect to…" tiles (the
  accessible tree gives the tiles no names: use the visible text via `find` or a screenshot).
  Tiles seen: Garmin, Oura, Withings, Google Health, Google Fit, Apple Health, Health Connect,
  Dexcom, FreeStyle Libre, Omron, WHOOP, iHealth, Strava, Polar, Suunto, Sleep Number,
  Ultrahuman, Coros, Morpheus, Fitbit. A connected one shows "connected".
- Apps such as Medisafe, MyFitnessPal, Bearable come in through Apple Health / Health Connect /
  Google Fit or CSV (skill `import-csv`), not a tile.
- `/sources/provider`: health systems (patient-portal connection). Not mapped yet (U).
- Apple Health and Health Connect sync from the phone app, not the website.

## Steps

1. Which source, which profile. Check the name at top right.
2. `/sources/app/add` → the tile. Tell the user what will open; let them complete the sign-in.
3. Back on `/sources/app`, confirm it shows as connected. Report.
