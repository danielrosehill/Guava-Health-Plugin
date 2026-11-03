# guava-mcp: the MCP server

`guava-mcp` (extra `[mcp]`, module `guava_cli/mcp_server.py`) exposes the CLI as MCP tools.
It's meant to run where the tokens live, typically a home server behind an MCP gateway, so
every client (Claude Code on any machine, desktop or phone apps through the gateway) shares
one set of grants. Guava rotates refresh tokens on every use, so a grant can't be shared by
copying files between machines.

## Tools

`profiles`, `resolve`, `label_profile`, `whoami`, `auth_start`, `auth_finish`,
`log_medication`, `log_entry` (single or batch), `log_metric`, `search`, `fhir_read`, `schema`,
`version`. All of them return the CLI's JSON, and errors come back as
`{"error": …, "hint": …}` objects rather than exceptions.

`profile` (since 0.4.0) takes a label, a friendly name or an alias, and is optional: left
out, it means the grant with relation `self`, or the only grant. Names live in
`/data/profiles.json` next to `tokens/`. `auth_start` takes `name`, `relation` and `aliases`,
and `label_profile` sets them on an existing grant.

## Run

| How | Command |
|---|---|
| stdio, local | `MCP_TRANSPORT=stdio uvx --from 'guava-cli[mcp] @ git+https://github.com/danielrosehill/Guava-Health-Plugin' guava-mcp` |
| HTTP, local | `uvx --from '…[mcp] @ git+…' guava-mcp` → `http://0.0.0.0:3000/mcp` |
| Docker | `docker build -t guava-mcp .` then run with a volume at `/data` |

Env: `GUAVA_CLIENT_ID`, `GUAVA_CLIENT_SECRET`, optional `GUAVA_TEST_CLIENT_ID` /
`GUAVA_TEST_CLIENT_SECRET` (used for grants made with a test key), `GUAVA_HOME` (`/data` in the
image), `MCP_TRANSPORT` (`streamable-http` | `stdio`), `MCP_HOST`, `MCP_PORT` (3000),
`MCP_STATELESS` (`true`).

## Compose example (behind a gateway)

```yaml
  guava-mcp:
    build:
      context: ./vendor/guava-health      # this repo as a submodule
    container_name: guava-mcp
    environment:
      GUAVA_CLIENT_ID: ${GUAVA_CLIENT_ID}
      GUAVA_CLIENT_SECRET: ${GUAVA_CLIENT_SECRET}
      TZ: Asia/Jerusalem                  # your timezone: "now" and offset-less times use it
    volumes:
      - guava-data:/data                  # tokens; must persist
    mem_limit: 256m
    restart: always
    networks: [gateway]                   # no host port; only the gateway reaches it
volumes:
  guava-data:
```

Register with the gateway as streamable HTTP at `http://guava-mcp:3000/mcp`.

## Authorising on the server

Call `auth_start(profile="me")`. It returns a consent URL that lasts 10 minutes. The user
opens it on any device, signs in, **selects the profile** and approves. The browser then
fails to load `https://localhost:8765/callback?code=…`, which is expected: copy that URL
into `auth_finish(profile="me", redirect_url=…)`. Repeat for each dependent.

## Timezone

Times without an offset, and `"now"`, use the server's local timezone. Set `TZ` in the
container, or the entries land in UTC.
