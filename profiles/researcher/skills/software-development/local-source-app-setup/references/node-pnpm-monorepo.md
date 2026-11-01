# Node/pnpm Monorepo Setup Recipe

Use this as a compact checklist; repository docs remain authoritative.

## Runtime selection

```bash
uname -m
node --version
pnpm --version
```

Read root `package.json` for `engines.node` and `packageManager`. If a local Node runtime is needed, download the architecture-matching official archive, verify it against `SHASUMS256.txt`, and extract it under a user-local app/toolchain directory. Prefix commands with that runtime's `bin` directory.

```bash
PATH="$HOME/.local/node-24/bin:$HOME/.local/bin:$PATH" corepack install --global pnpm@10.33.2
PATH="$HOME/.local/node-24/bin:$HOME/.local/bin:$PATH" pnpm install --frozen-lockfile
```

Substitute versions from project metadata rather than copying these literally.

## Launch and verification

Use the repository-defined lifecycle command. For tools-dev-style projects:

```bash
PATH="$HOME/.local/node-24/bin:$HOME/.local/bin:$PATH" pnpm tools-dev start web --daemon-port 7457 --web-port 5175
curl -fsS http://127.0.0.1:7457/api/health
PATH="$HOME/.local/node-24/bin:$HOME/.local/bin:$PATH" pnpm tools-dev status web
```

Then inspect logs and fetch the web URL. Initial Next.js compilation can make the first request slow; verify logs and retry after compilation.

## Setting a default integration

Prefer a product API/CLI. Preserve unrelated settings, then read back:

```bash
curl -fsS -X PUT http://127.0.0.1:7457/api/app-config \
  -H 'Content-Type: application/json' \
  --data '{"agentId":"hermes"}'
curl -fsS http://127.0.0.1:7457/api/app-config
```

Also query the application's runtime discovery endpoint and verify the requested integration reports `available: true` with a real executable path.

## Pitfalls

- `Exec format error` after extraction usually means the archive architecture is wrong; map `aarch64` to `arm64`, not `x64`.
- A dependency install is not completion. Launch, health-check, inspect status/logs, verify integration discovery, and read settings back.
- Do not patch source defaults for a per-install preference when a persisted settings boundary exists.
