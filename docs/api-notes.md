# Guava API: working notes

Condensed from https://guavahealth.com/api-portal/documentation (signed-in page, read
2026-11-03). Confirmed means it's in the docs; tested means a real call succeeded. Nothing
is marked tested yet.

## Hosts

| Purpose | URL |
|---|---|
| Live API | `https://api.guavahealth.com` |
| Sandbox API | `https://api-test.guavahealth.com` |
| Authorize (browser) | `https://guavahealth.com/oauth/authorize` |

## OAuth 2.1

Confidential clients only. PKCE S256, Pushed Authorization Requests (PAR) and
refresh-token rotation are all mandatory. Send client credentials either as HTTP Basic or
as form fields, never both in the same request.

1. `POST /oauth/par`: `code_challenge`, `code_challenge_method=S256`, `scope`,
   `state`, `redirect_uri`. Returns `{request_uri, expires_in: 600}`.
2. Browser to `GET https://guavahealth.com/oauth/authorize?client_id=…&request_uri=…`.
   Comes back to `redirect_uri?code=…&state=…`.
3. `POST /oauth/token`: `grant_type=authorization_code`, `code`, `code_verifier`,
   optional `redirect_uri`, which must match the PAR one. Returns `access_token`,
   `refresh_token` (only with `offline_access`), `expires_in: 3600`, `scope`, `patient`.
4. Refresh: `grant_type=refresh_token`. You get a **new refresh token every time**:
   persist both before using either. If you reuse an old one after its replacement has
   been used, you get `invalid_grant` and must re-authorise.
5. `POST /oauth/revoke`, `token=…`. Returns 200 with an empty body.

Errors: `invalid_grant`, `invalid_client`, `invalid_request`, `invalid_scope` (scope
not enabled on the app), `access_denied`.

## Scopes

SMART-style: `.rs` read, `.cud` write, `.cruds` both. Data entries need `.c` per type.

## Reads

- `GET /v1/me`, scope `profile`. Returns `{user:{email}, profile:{id, given_name, family_name}}`.
- `POST /v1/{metrics|sleep|activities|nutrition|water}/_search`. The body is
  **form-urlencoded** (POST so PHI stays out of URLs). Params: `start_time`, `end_time`
  (ISO 8601 with offset; start inclusive, end exclusive), `_count`. For `metrics`,
  `types=a,b` is required.
  - These high-volume metric types must be requested on their own: steps, heart_rate_variability,
    resting_heart_rate, vo2_max, oxygen_saturation, respiratory_rate, blood_glucose, heart_rate.
  - `_count` maximum: 10000 for metrics, 1000 for the rest. Use a high value when
    paging through history, or you'll be rate limited.
  - Paging: `link[{relation:"next", url}]`. POST that URL as-is with **no body**.
  - Each entry has a `source` (e.g. `garmin.com`, an EHR host, or `guavahealth.com`
    for in-app logs). `timezone_unknown: true` marks UTC-only sources.
- `GET /fhir/R4/{Patient|Practitioner|AllergyIntolerance|Condition|Procedure|MedicationRequest|Immunization}`.
  Read-only, scope `patient/{Resource}.rs`.

## Writes

- `POST /v1/{metrics|sleep|nutrition|water|activities}` with
  `{source, log_type: auto|manual, entries:[…]}`, up to 10000 entries. Meant for
  device/app-sourced data. Units are UCUM (`kg`, `[lb_av]`, `Cel`, `[degF]`, `mm[Hg]`,
  `mg/dL`, `mmol/L`, `mL`, `[foz_us]`, `kcal`, `km`…). Blood pressure is two metric
  types: `systolic_blood_pressure` and `diastolic_blood_pressure`.
- `POST /v1/data-entries` with `{type, entries:[…]}`, for self-reported logs. They
  behave like in-app logs (the user can edit and delete them in the app).
  - `med_usage`: `time`, `medication_name`, `quantity` (0.001–1000, default 1).
    Creates the medication if the name is new.
  - `symptoms`: `time`, `symptom_name`, `severity` 0–10. Creates the symptom if the name is new.
  - `mood` 1–5 + `tags`, `energy` 1–5, `journal` (`notes` required),
    `bowel_movement` (`bristol_type` 1–7, `tags`, `end_time`), `menstrual_cycle`
    (`flow`), `sexual_activity` (18+ only).
  - Any entry: `notes` (up to 10000 chars) and `identifier: [{value, system?}]` for
    idempotency. A repeated identifier is skipped and not counted in `accepted`.
- Response: `{accepted, environment}`.
- Compression: send and accept `zstd` or `gzip`. Recommended for bulk.

## Gaps (2026-11-03)

No read of data entries, no update or delete, no medication management, and only 7 FHIR
resources even though the form offers 15. The form has no `profile` checkbox, although
`/v1/me` documents that scope.
