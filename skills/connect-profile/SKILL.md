---
name: connect-profile
description: 'Authorise the Guava Health API for one profile, the account holder or a dependent such as a child on a family plan, and store its tokens under a short label. Use for "connect Guava", "add my son/daughter", "authorise my daughter''s profile", "re-login to Guava", invalid_grant errors, or listing which profiles are connected.'
license: MIT
compatibility: Python 3.9+, openssl (or use --paste), GUAVA_CLIENT_ID and GUAVA_CLIENT_SECRET in the environment. Uses the guava CLI from this repo (uv tool install).
---

# Connect a profile

One grant equals one Guava profile. There is no family scope: a dependent is a separate
grant, chosen on Guava's consent screen. See `docs/family-and-dependents.md`.

Command: `guava` (package `guava-cli` from this repo). If `command -v guava` fails, install it:
`uv tool install 'git+https://github.com/danielrosehill/Guava-Health-Plugin'`
(add the `[nfc]` extra for tag writing). Prefix calls with the secrets wrapper if credentials live there.

## Steps

1. `guava profiles` lists existing grants (label, Guava profile name, refresh-token present).
   If the requested person is already connected and `me` works, stop.
2. Pick a label: `me` for the holder, and the dependent's first name in lowercase for each
   dependent. Labels are local only.
3. Run `guava auth --profile <label>` in the background (it waits up to 300 s for the
   redirect). The consent URL is printed to stderr and opened in the browser.
4. Tell the user: sign in as the account holder and, **for a dependent, pick the
   dependent's profile on the consent screen**. With the localhost redirect, the browser
   warns about a self-signed certificate once. Proceed past it.
   **Remote / phone:** run `guava auth -p <label> --start`, which prints the URL and saves
   the pending state (it expires in 10 min). Send the URL to the user. They sign in and land
   on `https://localhost:8765/callback?code=…`, which fails to load. That's fine: they paste
   the full address back, and you run `guava auth -p <label> --finish '<url>'`.
5. On success the command prints `granted_scopes` and `me`. Check that `me.profile` is the
   intended person (holder vs child). If it's wrong, `guava revoke --profile <label>` and redo.
6. If `invalid_scope` comes back, the app has fewer scopes than `guava_cli/scopes-full.txt`.
   Retry with `--scopes "<the app's scope list>"`.

Record anything new about the dependent flow in `docs/family-and-dependents.md`
(under "Unverified, check on first real grant") with the date.
