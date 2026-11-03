# Family plans and dependents

Status: from Guava's API documentation and a real live grant for a holder and a dependent
child (2026-11-03). The remaining open points are listed at the end.

## The short version

Guava has **no family, household or dependent scope**. A grant is always for **one
profile**. A parent on a family plan who wants to manage their child's data does this:

1. Create one API app (see `docs/creating-the-api-app.md`). The scopes you tick apply to
   every profile you will grant for, so pick them for the union of what you want to do
   for yourself and for the child.
2. Run the OAuth flow **once for yourself**: `guava.py auth --profile me`.
3. Run it **again for the child**: `guava.py auth --profile child`. Sign in as the same
   account holder; on Guava's consent screen choose the child's profile.
4. The plugin stores one token pair per label. Every command takes `--profile <label>`.

## How this shows up in the API

- `GET /v1/me` returns `user` (the granting account, by email) and `profile` (the
  subject the token acts on). The docs say profile is "the same person on a self-grant, a
  dependent when a manager acts on their behalf". So for the child's grant, `user` is
  the parent and `profile` is the child.
- `launch/patient` ("Patient ID for this connection" on the form) adds a `patient` id
  to token responses. This is the FHIR Patient id of the granted profile, so the
  holder's and the child's grants have different ids.
- Writes to `/v1/data-entries` land as if that profile had logged them in the app, and
  are editable and deletable there.
- `sexual_activity` entries are refused for profiles under 18. The other types have no
  documented age rule.

## Choosing scopes with a child in mind

The form groups scopes as Activity & fitness, Vitals, Body composition, Logging and
Clinical records. For a parent tracking a young child, the useful rows are usually:

| Need | Form row | Box |
|---|---|---|
| Log each dose given | Logging → Medication usage | Write (+ Read) |
| See prescribed meds | Clinical → Medications | Read |
| Fever log | Vitals → Body temperature | Read + Write |
| Growth | Body composition → Weight, Height | Read + Write |
| Symptoms (cough, rash, vomiting) | Logging → Symptoms | Write (+ Read) |
| Notes for the doctor | Logging → Journal entries | Write |
| Allergies, vaccinations | Clinical → Allergies, Immunizations | Read |

Ticking more than this does no harm: on the consent screen the user can decline
individual scopes, and does so per grant. You can grant the child a narrower set than
yourself by declining rows when you authorise their profile, or by passing
`--scopes` with a shorter list.

## What the API cannot do (2026-11-03)

- **No read endpoint for self-logged entries.** You can write `med_usage`, `symptoms`,
  `mood`, `energy`, `journal` and so on, but there is no documented
  `/v1/data-entries/_search`. Reads exist for metrics, sleep, activities, nutrition,
  water and a few FHIR resources. The form offers read scopes for the logging rows
  anyway; tick them so the grant is ready when Guava adds the endpoints.
- **No edit or delete.** Writes are append-only from the API. Correct or remove an entry
  in the Guava app. To avoid duplicates on retry, send an `identifier`
  (`guava.py ... --id <key>`). Guava ignores an entry that reuses one.
- **No managing a medication's details** (dose, schedule, stopping it). `med_usage`
  creates the medication by name if it doesn't exist. Use the exact name already in the
  profile to avoid creating near-duplicates.

## Tested on live (2026-11-03)

- **The consent screen makes you select the profile.** Sign in as the account holder, pick
  yourself or the dependent, then approve. No profile switch beforehand is needed.
- The dependent's grant returned `/v1/me` with `user` = the holder's email and `profile` =
  the child, a different `patient` id from the holder's, and the same 45 scopes. FHIR
  `MedicationRequest` for the child returned the child's own records.
- Guava's tag-setup dialog (DIY NFC tags) has the same kind of profile picker, listing the
  holder and the dependents.

## Still open
- ~~Whether `/v1/me` needs the `profile` scope~~: `profile` is granted automatically (sandbox, 2026-11-03).
- The sandbox (test client) always grants a synthetic test patient, so the dependent flow
  can only be checked with a live client.
- Whether one refresh token per profile is independent (expected, since they are separate grants).

Record what you find here, with the date.
