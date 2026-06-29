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

### 2. Ensure the web UI is built

The dashboard serves static assets from `web/dist`. On a fresh checkout, a reinstall, or after certain migrations, this directory may be missing. The CLI does **not** auto-build it on `--no-open` non-interactive runs.

If missing:

```bash
cd /path/to/hermes-agent/web
npm install   # only if node_modules/dist are absent
npm run build
```

> **Pitfall:** `npm run build` can fail with a clean-install `Cannot find module '../lib/tsc.js'` if `node_modules` is incomplete. Run `npm install` first.

### 3. Start the service in the background

For agent/headless contexts, pass both `--no-open` (skip browser popup) and `--insecure --host 0.0.0.0` if remote access is expected. Omit `--insecure --host 0.0.0.0` for localhost-only.

```bash
hermes dashboard --host 0.0.0.0 --insecure --no-open
```

### 4. Verify with an HTTP probe (not process status alone)

`hermes dashboard --status` lists PIDs, but a listed process does not guarantee the HTTP server is healthy. Use curl against the port (default `9119`).

```bash
sleep 2
curl -s -o /dev/null -w "%{http_code}" http://localhost:9119
# Expect 200
```

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
| Start dashboard (bg, no-browser) | `hermes dashboard --host 0.0.0.0 --insecure --no-open` |
| Install gateway service | `hermes gateway install` |
| Gateway status | `hermes gateway status` |
| Restart profile gateway | `systemctl --user restart hermes-gateway-<profile>.service` |
| Verify HTTP | `curl -s -o /dev/null -w "%{http_code}" http://localhost:<port>` |

## Troubleshooting signals

- **`Cannot find module '../lib/tsc.js'` during build** → `cd web && npm install` before `npm run build`
- **Port not listening after start** → check `web/dist` exists; rebuild; stop stale processes first
- **`hermes gateway restart` inside gateway hangs** → use `systemctl --user restart` from another session, or `kill -9` then start
- **Gateway dies on SSH logout** → `sudo loginctl enable-linger $USER`

## References

- `references/dashboard.md` — deeper frontend build troubleshooting, npm quirks, and confirmed build commands