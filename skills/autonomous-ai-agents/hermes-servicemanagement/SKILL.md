---
name: hermes-servicemanagement
description: "Manage Hermes background services (dashboard, gateway) as long-lived daemons."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, dashboard, gateway, services, background, daemon]
    homepage: https://github.com/NousResearch/hermes-agent
---

# Hermes Service Management

Run, stop, verify, and troubleshoot Hermes background services — especially the web dashboard and messaging gateway — as detached daemons.

## When to use this skill

- User asks to **run the dashboard in the background**
- User asks to **start/stop/restart the gateway service**
- User wants to **check status** or **verify** that a Hermes service is actually serving
- You need to **clean up stale Hermes service processes** before starting a fresh one

Core covered service: `hermes dashboard`. Principles here also apply to `hermes gateway`.

## Standard workflow: Hermes Dashboard

### 1. Clean up stale processes

Old dashboard processes from prior sessions often survive. Always stop them first.

```bash
hermes dashboard --stop
```

Pitfall: if `hermes` CLI wrapper is unavailable, replace with the explicit venv Python:
```bash
/home/ubuntu/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main dashboard --stop
```

### 2. Ensure the web UI is built

The dashboard serves static assets via `web_dist` (the server resolves this at `hermes_cli/web_dist` relative to the Python package root). On a fresh checkout, reinstall, or after certain migrations, this directory may be missing. The CLI does **not** auto-build it on `--no-open` non-interactive runs.

If missing:

```bash
cd /home/ubuntu/.hermes/hermes-agent/web
npm install   # only if node_modules/dist are absent
npm run build
```

> **Pitfall:** `npm run build` can fail with a clean-install `Cannot find module '../lib/tsc.js'` if `node_modules` is incomplete. Run `npm install` first.
> **Pitfall:** the Vite build outDir is `../hermes_cli/web_dist/` relative to `hermes-agent/web/`, i.e. `/home/ubuntu/.hermes/hermes-agent/hermes_cli/web_dist/`. Do not run `npm run build` from anywhere else.

### 3. Start the service in the background

The explicit, portable command:

```bash
cd /home/ubuntu/.hermes && /home/ubuntu/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main dashboard --port 9119 --no-open
```

For remote access, do **not** rely on `--insecure --host 0.0.0.0`. Newer Hermes versions enforce auth on non-loopback binds; `--insecure` no longer bypasses it. Instead, either configure `dashboard.basic_auth` in `config.yaml` or keep the dashboard on `127.0.0.1` and reach it through a reverse proxy/tunnel.

#### Enabling remote binds with basic auth

If you need the dashboard accessible from the network/Tailscale, set `dashboard.basic_auth` in `config.yaml`:

```yaml
dashboard:
  basic_auth:
    username: youruser
    password_hash: '<hash>'
```

Generate the hash from the Hermes venv:

```bash
/home/ubuntu/.hermes/hermes-agent/venv/bin/python -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('your-password'))"
```

Then restart the systemd service if one exists, or restart the dashboard process. Without this, the dashboard process will refuse to start on `0.0.0.0` and the service will loop-restart forever.

### 4. Verify with an HTTP probe (not process status alone)

`hermes dashboard --status` lists PIDs, but a listed process does not guarantee the HTTP server is healthy. Use curl against the port (default `9119`).

```bash
sleep 2
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9119
# Expect 200
ss -tlnp | grep 9119
```

**Pitfall:** `/api/version` returns `Unauthorized` from a bare curl because API auth uses the ephemeral session token injected into the SPA HTML (`window.__HERMES_SESSION_TOKEN__`). That 401 is **expected** and not a failure. Verify health with the root `/` path only, or confirm the token is present in the HTML.

### 5. Report the running PIDs and URL

Return the live PIDs and the direct URL so the user can reach it.

## Standard workflow: Hermes Gateway

- Install as a systemd user service: `hermes gateway install`
- Control: `hermes gateway start | stop | restart | status`
- Multi-profile routing: restart per-profile with `systemctl --user restart hermes-gateway-<profile>.service`
- **Pitfall:** Running `hermes gateway restart` *from inside* the gateway is blocked. Use `systemctl --user restart` or `hermes gateway restart` from a different shell session.
- **Pitfall:** systemd may hang on SIGTERM. If `restart` stalls, kill the old PID with `kill -9` then `start`.

## Key commands reference

| Action | Command |
|---|---|
| Stop dashboard | `hermes dashboard --stop` |
| Dashboard status | `hermes dashboard --status` |
| Start dashboard (bg, no-browser) | `cd /home/ubuntu/.hermes && /home/ubuntu/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main dashboard --port 9119 --no-open` |
| Install gateway service | `hermes gateway install` |
| Gateway status | `hermes gateway status` |
| Restart profile gateway | `systemctl --user restart hermes-gateway-<profile>.service` |
| Verify HTTP | `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:<port>` |

## Troubleshooting signals

- **`Cannot find module '../lib/tsc.js'` during build** → `cd web && npm install` before `npm run build`
- **Port not listening after start** → check `web_dist` exists at `hermes-agent/hermes_cli/web_dist/`; rebuild; stop stale processes first
- **Dashboard service restarts continuously with `Refusing to bind dashboard to 0.0.0.0`** → non-loopback binds now always require `dashboard.basic_auth` in `config.yaml`. Add a username + `password_hash`, then restart. `--insecure` no longer bypasses this.
- **`hermes gateway restart` inside gateway hangs** → use `systemctl --user restart` from another session, or `kill -9` then start
- **Gateway dies on SSH logout** → `sudo loginctl enable-linger $USER`
- **`hermes dashboard --status` shows PIDs but HTTP is closed** → stale PID is lying; stop all and restart fresh
- **Trying `python -m hermes_cli.main web`** → invalid subcommand; use `dashboard`
- **`/api/version` returns 401** → expected; token auth is injected into `index.html`, not sent on bare API calls. Use root `/` probe instead.

## References

- `references/dashboard.md` — deeper frontend build troubleshooting, npm quirks, and confirmed build commands
- `references/auth.md` — session token injection behavior and why bare `/api/*` curls 401