---
name: connect-profile
description: 'Authorise the Guava Health API for one profile, the account holder or a dependent such as a child on a family plan, and store its tokens under a short label. Use for "connect Guava", "add my son/daughter", "authorise my daughter''s profile", "re-login to Guava", invalid_grant errors, or listing which profiles are connected.'
license: MIT
compatibility: Python 3.9+, openssl (or use --paste), GUAVA_CLIENT_ID and GUAVA_CLIENT_SECRET in the environment. Uses scripts/guava.py.
---

# Connect a profile

One grant equals one Guava profile. There is no family scope: a dependent is a separate
grant, chosen on Guava's consent screen. See `docs/family-and-dependents.md`.

`G="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/guava.py"`. If credentials live in a secrets
wrapper, prefix every call with it (e.g. `with-secrets $G …`).

## Steps

1. `$G profiles` lists existing grants (label, Guava profile name, refresh-token present).
   If the requested person is already connected and `me` works, stop.
2. Pick a label: `me` for the holder, and the dependent's first name in lowercase for each
   dependent. Labels are local only.
3. Run `$G auth --profile <label>` in the background (it waits up to 300 s for the
   redirect). The consent URL is printed to stderr and opened in the browser.
4. Tell the user: sign in as the account holder and, **for a dependent, pick the
   dependent's profile on the consent screen**. With the localhost redirect, the browser
   warns about a self-signed certificate once. Proceed past it.
   If the user is on another machine or the listener can't bind, use `--paste --no-browser`
   and have them paste the final URL.
5. On success the command prints `granted_scopes` and `me`. Check that `me.profile` is the
   intended person (holder vs child). If it's wrong, `$G revoke --profile <label>` and redo.
6. If `invalid_scope` comes back, the app has fewer scopes than `reference/scopes-full.txt`.
   Retry with `--scopes "<the app's scope list>"`.

Record anything new about the dependent flow in `docs/family-and-dependents.md`
(under "Unverified, check on first real grant") with the date.
