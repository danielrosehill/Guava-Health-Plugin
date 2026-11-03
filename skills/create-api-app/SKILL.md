---
name: create-api-app
description: 'Fill in Guava Health''s "New API App" form for the user in their signed-in browser: name, redirect URI, purpose and the scope checkboxes for a chosen preset (family-manager, medication-logger, read-only-review). Use for "set up the Guava API", "create my Guava app", "which scopes should I tick", or when no GUAVA_CLIENT_ID exists yet. Stops before Create App.'
license: MIT
compatibility: Claude Code with a browser tool (Claude in Chrome or similar) and the user signed in to guavahealth.com with API access enabled. Reads reference/app-form.json.
---

# Create the Guava API app

The form map is `reference/app-form.json`. It's the source of truth for labels, scope
strings and presets. Background for humans: `docs/creating-the-api-app.md`.

## Steps

1. Ask only what you can't infer:
   - **Preset.** Default `family-manager` when the user mentions children, dependents or
     a family plan, or wants to both log and review. Otherwise `medication-logger` or
     `read-only-review`.
   - **App name** (suggest `<First name> Health Agent (personal CLI)`).
   - **Redirect URI.** Default `https://localhost:8765/callback`, unless the user already
     has `GUAVA_REDIRECT_URI` set.
2. Open `https://guavahealth.com/api-portal/apps`. If it redirects to sign-in or to the
   API marketing page, stop: the user must sign in or join the API platform themselves.
3. Click **New App** by element reference. A dialog opens.
4. Fill **App Name**, **Redirect URIs** and **Purpose**, using the `template` in
   `app-form.json`. Fill `{dependents_clause}` with e.g. " and their dependent child's
   profile" when relevant. Never put names, dates of birth or conditions into Purpose.
5. Tick the preset's boxes. They are `role=checkbox` buttons, so click them by reference,
   in row order. Every row has a `Read` and a `Write` checkbox, so locate them through the
   row's label, not the bare word "Read".
6. Read the **Resulting scope string** textbox and compare it with the preset (for
   `family-manager`, the content of `reference/scopes-full.txt`, 44 lines). Fix any difference.
7. Do **not** click Create App. Show the user the name, redirect URI and scope count, and
   ask them to review and click it themselves (some agent harnesses block this click anyway).
8. After creation, the portal shows a client id and a secret. Tell the user to store them in
   their secrets manager as `GUAVA_CLIENT_ID` and `GUAVA_CLIENT_SECRET`. Never read the
   secret aloud, paste it into chat or write it to a file in this repo.
9. Next: the `connect-profile` skill.

If a label from `app-form.json` is missing, the form changed. Say
`CHANGED: <label> not found`, map the new form and update `app-form.json` and
`docs/creating-the-api-app.md` with the date.
