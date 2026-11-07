# Guava API: working notes

Condensed from https://guavahealth.com/api-portal/documentation (signed-in page, read
2026-11-03). Confirmed means it's in the docs; tested means a real call succeeded.

## Hosts

| Purpose | URL |
|---|---|
| Live API | `https://api.guavahealth.com` |
| Sandbox API | `https://api-test.guavahealth.com` |
| Authorize (browser) | `https://guavahealth.com/oauth/authorize` |

## Tested 2026-11-03 (beyond the docs)

- **User-Agent is required.** Cloudflare answers `403 error code: 1010` to Python's default
  `Python-urllib/x` agent on both hosts. Any named agent works.
- **Test clients only work on the sandbox.** Ids look like `guava_test_client_…`. On
  `api.guavahealth.com` they get `invalid_client`, and on `api-test.guavahealth.com` they are
  accepted. `guava` infers `GUAVA_ENV=test` from that prefix.
- **PAR needs `response_type=code` and `client_id` in the form body**, even with HTTP
  Basic client auth. Without `client_id`: `invalid_request "client_id is required."`.
  Without `response_type`: `unsupported_response_type`.
- PAR with all 44 scopes of `guava_cli/scopes-full.txt` returns `201 {request_uri, expires_in: 600}` on the sandbox.
- **Sandbox grants a synthetic test patient**, not your real profile. The consent flow
  signs you in with your real Guava account, but the grant is for a fixture patient (with
  its own `/v1/me` name and FHIR Patient id) that already has metrics, sleep, activities,
  nutrition, 12 MedicationRequests and 3 AllergyIntolerances. So holder and dependent
  grants can only be tested with a live client.
- **The full sandbox loop works** (2026-11-03): PAR → consent → `--finish` → token
  (`refresh_token` and `patient` included) → `/v1/me` → all five `_search` reads → FHIR
  `Patient`, `MedicationRequest` and `AllergyIntolerance` → writes to `/v1/data-entries`
  (`med_usage`) and `/v1/metrics` (`body_temperature`), each `{"accepted":1,"environment":"test"}`.
- **`profile` is granted automatically.** Token `scope` came back with the 44 requested
  plus `profile`, although the form has no box for it. `/v1/me` works.
- **Identifiers did not dedupe in the sandbox.** Posting the same `med_usage` entry twice
  with the same `identifier` returned `accepted: 1` both times, although the docs say a
  repeat is ignored. Don't rely on `--id` alone to prevent duplicates. Untested on live.
- **Units in reads can differ from write units.** A sandbox weight came back as
  `{"value":56310,"unit":"g"}`. Read `unit` on every entry rather than assuming `kg`.
- **Some sleep timestamps have no offset** (e.g. `2026-08-06T22:42:00`), despite the docs.
- **Live keys need production approval.** A new app is in status "Development" with test keys
  only. Its page (`/api-portal/app/<appId>`) has **Submit for production approval**. Until
  that is approved, "Create live key" is disabled ("Submit your app for production approval
  to enable live keys"). You can create more test keys and edit the scopes there later.

## Tested 2026-11-07 (live)

- **A new medication name works on live.** A `med_usage` entry with an unused name returned
  `{"accepted":1,"environment":"live"}`, and the medication appeared straight away in
  `GET /fhir/R4/MedicationRequest`: status `active`, no dose text, shown as app-entered.
- **App-entered names can carry trailing spaces** (seen on live, e.g. `"Lexapro "`). Matching is
  by exact name, so pass the name exactly as `guava meds` returns it. Whether a trimmed name
  creates a duplicate is untested.

- **No dose history, last-taken or reminder read (re-probed 2026-11-07, live).** 404 on
  `POST /v1/data-entries/_search` (with and without `type=med_usage`), `POST /v1/med_usage/_search`,
  `POST /v1/med-usage/_search`, `POST /v1/medications/_search`, `GET /v1/reminders`,
  `GET /v1/medication-reminders`, `GET /v1/schedules`, `POST /v1/reminders/_search`, and FHIR
  `MedicationAdministration`, `MedicationStatement`, `MedicationDispense`, `Task` and `CarePlan`.
- **`MedicationRequest` carries no usable schedule (live, one account, 18 entries).** Dosing fields
  present: `dosageInstruction[].text` (12 entries) and `timing.repeat.boundsPeriod.start` (6). No
  frequency, time of day or next-due field.
- **`GET /fhir/R4/Observation` returns 200 on live**, although it isn't in the documented list. Its
  contents were not inspected.

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

## What the plugin builds on top (0.5.0, 2026-11-03)

- `guava meds` flattens `GET /fhir/R4/MedicationRequest` into name, status, dose
  (`dosageInstruction[].text`), as-needed, start (`timing.repeat.boundsPeriod.start`), source,
  RxNorm and notes. Observed on sandbox and live 2026-11-03: hand-entered medications have no
  `meta.tag`; clinical ones carry the record source in `meta.tag[].display` (sandbox: "Demo
  Hospital"). `source` is "Guava app" when the tag is absent; that rule is inferred from those
  two accounts. FHIR Bundles are followed through `link[next]` (not observed in practice yet:
  the 12-entry sandbox list came back in one page).
- `guava dose-log`: since there is no read for data entries, every accepted `med_usage` write
  is appended to `$GUAVA_HOME/dose-log.jsonl` (0600). It only knows doses written through
  this client on that machine or MCP server.
- `guava water --ml N` posts `{source, log_type: manual, entries:[{time, volume:{value, code:"mL"}}]}`
  to `/v1/water`. Built from the docs' write format; dry-run checked, **not yet tested** against the API.
- Medication notes: `MedicationRequest.note[].text` is read-only, and no endpoint sets it
  (see Gaps). Notes can go on a dose entry (`notes`) or a `journal` entry instead.

## Gaps (2026-11-03)

No read of data entries, no update or delete, no medication management, and only 7 FHIR
resources even though the form offers 15.

**Tested 2026-11-03, live and sandbox, with valid bearer tokens:**

| Request | Result |
|---|---|
| `GET /v1/medications`, `GET /v1/medications/{id}`, `POST /v1/medications`, `POST /v1/medications/_search` | 404 `not_found "No such endpoint."` |
| `GET /v1/medication`, `/v1/meds`, `/v1/med-usage`, `/v1/symptoms`, `/v1/entries`, `/v1/profiles`, `/v1/dependents` | 404 |
| `POST /v1/data-entries/_search`; `GET`, `PATCH`, `DELETE /v1/data-entries/{id}` | 404 |
| `GET`, `PUT`, `PATCH`, `DELETE /v1/data-entries` | 405 `method_not_allowed` (the path exists, POST only) |
| `GET`, `DELETE /v1/metrics` | 405 |
| `GET /fhir/R4/MedicationStatement`, `GET /fhir/R4/metadata` | 404 OperationOutcome "Unsupported resource type." |
| `GET /openapi.json`, `/v1/openapi.json` | 404 |

Reading the medication list does work, through FHIR: on live (2026-11-03, a dependent's
grant, no clinical portal connected) `GET /fhir/R4/MedicationRequest` returned the
medications entered by hand in the Guava app: `status: active`, `intent: plan`,
`requester` and `reportedReference` = the profile's own Patient, name in
`medicationCodeableConcept.text`, the dose typed in the app in `dosageInstruction[].text`,
and its notes in `note[].text`. So it is not limited to portal prescriptions.

So a medication can only be created implicitly, by a `med_usage` entry with a new name.
Listing, editing and deleting medications, and reading, editing or deleting doses, need the
Guava app. A 405 rather than a 404 is the sign that a path exists; use that when re-probing. The form has no `profile` checkbox, although
`/v1/me` documents that scope.
