---
name: setup
description: 'End-to-end setup of the unofficial Guava Health integration: install the guava CLI, create the Guava API app, store credentials, connect the account holder and any dependents, then optionally deploy it as an MCP server, either locally in Claude Code or as a container behind an MCP gateway on a home server. Use for "set up Guava", "install the Guava plugin", "deploy Guava as an MCP", "put Guava on my gateway".'
license: MIT
compatibility: uv and Python 3.9+. A Guava account with API access. For the gateway route, Docker on the server and an MCP gateway or client that speaks streamable HTTP.
---

# Set up Guava

Unofficial integration, not made by Guava Health, Inc. Work through the stages in order,
skip any that are already done, and confirm the route with the user at stage 5.

## 1. CLI

`command -v guava || uv tool install 'git+https://github.com/danielrosehill/Guava-Health-Plugin'`.
Add `[nfc]` (`'guava-cli[nfc] @ git+…'`) if they want DIY tags. Check with `guava version`.

## 2. API app

If no client id exists yet, run the `create-api-app` skill (the form is in
`reference/app-form.json`). New apps get **test** keys (sandbox, synthetic patient only).
For real data: app page → **Submit for production approval** (was instant for a personal
app on 2026-11-03) → **Create live key**. The user clicks the key-creation buttons.

## 3. Credentials

The user stores `GUAVA_CLIENT_ID` and `GUAVA_CLIENT_SECRET` in their secrets manager. If they
keep the sandbox key too, it goes in `GUAVA_TEST_CLIENT_ID` / `GUAVA_TEST_CLIENT_SECRET`. Never
echo a secret back or write it to a repo. Expose the variables to wherever `guava` or
`guava-mcp` will run (stage 5 decides where).

## 4. Profiles: decide where the grants live first

Guava rotates the refresh token on every use, so **each grant must live in exactly one
place**. Two machines sharing a copy will lock each other out. So:
- CLI-only or local MCP: connect on that machine (`connect-profile` skill).
- Gateway: connect **on the server**, through the MCP tools `auth_start` / `auth_finish`
  once it's deployed (stage 5c). Or **move** (never copy) existing token files from
  `~/.config/guava-health/tokens/` into the server's volume, then delete the local copies.

Then ask: **just you, or you and people you manage in Guava** (children, dependents)?
- **Single person:** one grant, `--profile me --name <Name> --relation self`. Every later
  command can leave `--profile` out.
- **Family:** that grant, plus one per dependent:
  `--profile <firstname> --name <Name> --relation dependent --alias "my son"`. On the consent
  screen the user must **select that dependent's profile**. Afterwards the user can say "check
  <Name>'s medications" or "log a dose for my son" and the skills pick the grant.
Run each grant through the `connect-profile` skill. To add a dependent later, run it again.

## 5. Route

Ask which one they want:

**a. CLI only.** Done. The other skills call `guava`.

**b. Local MCP (Claude Code on this machine):**
```
claude mcp add guava -e GUAVA_CLIENT_ID=… -e GUAVA_CLIENT_SECRET=… -e MCP_TRANSPORT=stdio \
  -- uvx --from 'guava-cli[mcp] @ git+https://github.com/danielrosehill/Guava-Health-Plugin' guava-mcp
```
Prefer the user's secrets wrapper over literal `-e` values. Tokens stay in `~/.config/guava-health`.

**c. Gateway (home server, shared by every client):**
1. On the server, build the image from this repo (`Dockerfile`, or add the repo as a
   submodule of the gateway's deployment repo and build from it). Run it on the gateway's
   Docker network with no host port. Mount a **named volume or bind mount at `/data`**: the
   tokens live there and must survive recreates. Pass the two credentials as env.
   Example compose service in `docs/mcp-server.md`.
2. Register it with the gateway as **streamable HTTP** at `http://<container>:3000/mcp`.
   Add it to the groups/namespaces of the people who should reach it. Health data is
   personal, so don't put it in a shared namespace unless the user asks.
3. From a new session, call `version` and `profiles` through the gateway (tools appear as
   e.g. `mcp__gateway__guava__profiles`). Then `auth_start` for each profile, have the user
   open the URL, select the profile, approve and paste back the redirect URL, and finish with
   `auth_finish`.
4. Remove any local grants for the same profiles (`guava revoke -p <label>` only revokes that
   machine's grant), so only the server holds tokens.

## 6. Verify

`profiles` lists each grant with the right `name` and `relation` (fix with `label_profile` /
`guava label`). `whoami` / `guava me -p <label>` for each profile shows the right person, then one read (e.g.
`search metrics --types weight`). Don't write test entries to real profiles. Use `dry_run`.
