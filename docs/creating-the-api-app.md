# Creating the Guava API app

Observed 2026-11-03. Machine-readable version: `reference/app-form.json`.
An agent can fill it for you with the `create-api-app` skill.

## Before you start

- A Guava account. API access to your own data is free. Business use goes through Guava.
- Sign up for the API platform at https://guavahealth.com/api. It then appears at
  https://guavahealth.com/api-portal (sections: API Apps, Organization, Documentation).
- Guava only issues **confidential clients**: something has to keep the client secret.
  A script on your own machine counts, a browser-only or mobile app does not.

## The form (API Apps → New App)

| Field | What to enter |
|---|---|
| App Name | Anything. Users see it on the consent screen. |
| Redirect URIs | One per line, **exact match**. For this plugin: `https://localhost:8765/callback`. It must equal `GUAVA_REDIRECT_URI`. |
| Purpose | Free text "for internal review": what the app does and why it needs the scopes. |
| Long-lived background access | `offline_access`. Tick it, or you get no refresh token and must sign in again every hour. |
| Patient ID for this connection | `launch/patient`. Tick it. It identifies which profile (you or a dependent) a grant is for. |
| Scope grid | One row per data type, each with **Read** and **Write**. Read alone gives `.rs`, Write alone `.cud`, both `.cruds`. |
| Resulting scope string | Read-only. Check it before you submit. |

Then **Create App**. The portal shows a client id and a client secret: store both in your
secrets manager straight away and export them as `GUAVA_CLIENT_ID` / `GUAVA_CLIENT_SECRET`.

## Test keys first, live keys after approval (2026-11-03)

Create App gives a **Development** app with a **test** key (`guava_test_client_…`). It only
works against the sandbox, which serves a synthetic patient. To reach real profiles, open
the app in API Apps and click **Submit for production approval** (then OK in the confirm
prompt). For a personal app it was approved **instantly** (2026-11-03): status changed to
"Approved for production". Write Purpose before you submit; see the README for the
framing (personal, non-commercial, single-user). Once it's approved,
**Create live key**, then store the live id and secret (`GUAVA_ENV` is inferred from the
id prefix). Redirect URIs and scopes stay editable on the same page (**Save changes**).

## Which boxes

For a holder who also manages dependents, the plugin's default (`family-manager` preset,
44 scopes, `reference/scopes-full.txt`):

- Both top-level boxes.
- Read + Write on every row in Activity & fitness, Vitals, Body composition and Logging.
- Read only on every row in Clinical records. The FHIR API is read-only, so Write
  there does nothing.

Narrower presets (`medication-logger`, `read-only-review`) are in `reference/app-form.json`.
If you tick fewer boxes than `scopes-full.txt`, `guava.py auth` fails with
`invalid_scope`. Pass `--scopes "<your list>"`, or edit a copy of the file and use `--scopes-file`.

## Redirect URI choices

Guava is https-only. Options, best first:

1. `https://localhost:8765/callback` (default). `guava.py auth` serves it with a
   self-signed certificate it makes in `~/.config/guava-health/localhost-cert/`. The
   browser warns once; proceed and the code is captured.
2. Same URI with `guava.py auth --paste`. Don't run a listener: after consent the browser
   shows an error page, so copy the URL from the address bar and paste it in.
3. A real https page you own that echoes the query string. Use `--paste`.

## Sandbox

Guava runs a test API at `https://api-test.guavahealth.com`. Set `GUAVA_ENV=test`.
Write responses report `"environment": "live"` or `"test"`, so check it on your first write.
