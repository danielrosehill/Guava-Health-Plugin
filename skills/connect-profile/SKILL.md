---
name: connect-profile
description: 'Authorise the Guava Health API for one profile, the account holder or a dependent such as a child on a family plan, and store its tokens under a short label. Use for "connect Guava", "add my son/daughter", "authorise my daughter''s profile", "re-login to Guava", invalid_grant errors, or listing which profiles are connected.'
license: MIT
compatibility: Python 3.9+, openssl (or use --paste), GUAVA_CLIENT_ID and GUAVA_CLIENT_SECRET in the environment. Uses the guava CLI from this repo (uv tool install).
---

# Connect a profile

One grant equals one Guava profile. There is no family scope: a dependent is a separate
grant, chosen on Guava's consent screen. See `docs/family-and-dependents.md`.

If the guava MCP tools are connected (through a gateway they appear as e.g. `mcp__gateway__guava__log_medication`; locally as `mcp__guava__…`), call those instead of the CLI: same arguments, same JSON.

Command: `guava` (package `guava-cli` from this repo). If `command -v guava` fails, install it:
`uv tool install 'git+https://github.com/danielrosehill/Guava-Health-Plugin'`
(add the `[nfc]` extra for tag writing). Prefix calls with the secrets wrapper if credentials live there.

## Steps

0. Grants live in exactly one place (Guava rotates refresh tokens). If the guava MCP server
   runs on a gateway, connect there with `auth_start` / `auth_finish`, not locally.

1. `guava profiles` (MCP `profiles`) lists existing grants with `label`, `name`, `relation`
   (`self` | `dependent` | `unknown`) and `aliases`. If the person is already connected and
   `guava me -p <label>` works, stop. If they are connected but unlabelled, go to step 7.
2. **Who is this grant for?** Ask, unless it's obvious:
   - **Single person:** the account holder only. Label `me`, relation `self`. Then
     `--profile` can be left out of every command.
   - **Family:** the holder (`me`, `self`), plus one grant per managed person: label = their
     first name in lowercase, relation `dependent`, aliases for how the user refers to them
     ("my son", "my daughter"). A dependent is anyone whose profile the holder manages in
     Guava (a child, or an adult they care for).
   Labels and names are local only (`$GUAVA_HOME/profiles.json`), never sent to Guava.
3. Start it in the background (it waits up to 300 s for the redirect):
   `guava auth --profile <label> --name <Name> --relation <self|dependent> [--alias "my son"]`
   The consent URL goes to stderr and opens in the browser.
   MCP: `auth_start(profile, name, relation, aliases)`.
4. Tell the user: sign in as the account holder and, **for a dependent, select the
   dependent's profile on the consent screen**. With the localhost redirect, the browser
   warns about a self-signed certificate once. Proceed past it.
   **Remote / phone:** add `--start`. That prints the URL and saves the pending state,
   including name and relation (it expires in 10 min). The user signs in and lands on
   `https://localhost:8765/callback?code=…`, which fails to load. That's fine: they paste the
   full address back, and you run `guava auth -p <label> --finish '<url>'`
   (MCP `auth_finish`).
5. The result has `name`, `relation`, `relation_inferred` and `me`. Check that `me.profile` is
   the intended person. `/v1/me` looks the same for the holder and a dependent (`user` is
   always the holder), so the API can't say which it is. If `relation_inferred` is true, the
   CLI guessed (first grant = `self`, later ones = `dependent`): confirm with the user and fix
   it in step 7. Wrong person: `guava revoke -p <label>` and redo.
6. If `invalid_scope` comes back, the app has fewer scopes than `guava_cli/scopes-full.txt`.
   Retry with `--scopes "<the app's scope list>"`.
7. **Label or relabel an existing grant** (no re-auth needed):
   `guava label -p <label> --name <Name> --relation dependent --alias "my son" --alias son`
   (MCP `label_profile`). `--clear-aliases` starts the alias list over.
8. Check the mapping: `guava resolve -p "<how the user says it>"` (MCP `resolve`) should
   return the right label.

Record anything new about the dependent flow in `docs/family-and-dependents.md` with the date.
