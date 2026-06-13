---
name: gateway-ops
description: "Operate and debug Hermes messaging gateways: restart lifecycle, inspect logs, diagnose unauthorized user drops, channel binding issues, and status checks across default + named profiles."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [gateway, discord, telegram, slack, systemd, logs, profiling]
---

# Gateway Ops

Class-level troubleshooting and operation for Hermes messaging gateways and per-profile gateway services.

## When to Use
- Bot is online but produces no reply / only reacts with emoji.
- Need to inspect active platforms, auth providers, and service state.
- Profile-specific gateway services need restart or status check.
- Permission/allowlist issues that silently drop messages before the model runs.

## Systemd Targets

| Profile | Service |
|---|---|
| default | `hermes-gateway.service` |
| named | `hermes-gateway-<name>.service` |

## Initial Status Check
```bash
hermes status --all
```
Shows active platforms, auth state, configured home channels, service PID, and whether allowlists are set. Always run this first when a platform is "connected but not responding".

Use `hermes status --all` under the active profile (default or `--profile <name>` from CLI). Note platform/ service mapping before touching config.

## Log Triage Sequence

1. Tail the latest logs only. Do not paginate the full history unless needed.
   ```bash
   tail -80 ~/.hermes/logs/gateway.log
   ```
2. If a named profile is suspected, check its log path:
   ```bash
   tail -80 ~/.hermes/profiles/<name>/logs/gateway.log
   ```
3. Search for failure signals:
   ```bash
   grep -iE 'Unauthorized|Error|Failed|Shutdown|exception' <path>
   ```

## Emoji-Only / No Reply on Discord

Fast diagnostic:
```bash
grep -i 'Unauthorized user' ~/.hermes/logs/gateway.log
grep -i 'Unauthorized user' ~/.hermes/profiles/<name>/logs/gateway.log
```

### Most common causes

1. Missing user allowlist
   - Fix: `GATEWAY_ALLOW_ALL_USERS=true` in the profile's env file (`~/.hermes/.env` or `~/.hermes/profiles/<name>/.env`).

2. Channel/thread not bound
   - Ensure the thread/channel/guild IDs are in the profile `config.yaml` (`discord.allowed_channels`, `discord.allowed_guilds`, etc.).
   - Threads inherit parent channel restrictions.

3. Change not applied yet
   - Changing env/config without restart leaves the running process on old state.

### Apply + verify

```bash
# default profile
systemctl --user restart hermes-gateway.service
# named profile
systemctl --user restart hermes-gateway-<name>.service
```

Verify:
```bash
systemctl --user status hermes-gateway-<name>.service
grep -i Unauthorized <path_to_gateway_log> | tail
```

Pitfall: calling `hermes gateway restart` from inside the running gateway session restarts itself, but on a named profile the systemd unit (`hermes-gateway-<name>.service`) is more reliable.

## References
- `references/discord-unauthorized-user.md` — full remediation recipe and verification checklist.

## Local Service Exposure (merged from local-service-access)

When the goal is exposing a locally-bound service reachable from other devices:

### A) Tailscale mesh access
- Bind to `0.0.0.0`; peer uses the host's Tailscale IP.
- Optional firewall restriction to Tailscale CIDR `100.64.0.0/10`.

### B) SSH tunnel
- Keep service bound to `127.0.0.1`.
- `ssh -L <local_port>:localhost:<service_port> user@host`

### C) Reverse proxy
- Keep service on localhost; let nginx/caddy expose with HTTPS/auth.

### Hermes dashboard applied example
- Active compose file: `~/.hermes/hermes-agent/docker-compose.yml`
- Change dashboard command host to `0.0.0.0` for Tailscale access.
- Do not update only `./hermes-config/...` or `/tmp/hermes-config/...` copies.

### Checklist
- [ ] Service is bound to the intended interface (`0.0.0.0` or tunnel).
- [ ] Firewall matches intended exposure.
- [ ] A peer on the allowed path can reach the service.
- [ ] Public internet exposure is not enabled unintentionally.

## Systemd Hosting for Gateways and Dashboards (merged from hermes-systemd-services)

When running Hermes components as systemd services on Oracle Linux or similar:

### Required unit shape
```
[Unit]
Description=...
After=network.target

[Service]
Type=simple
User=opc
Group=opc
Environment=HOME=/home/opc
Environment=USER=opc
WorkingDirectory=/home/opc
ExecStart=/home/opc/.hermes/hermes-agent/venv/bin/python3 \
          /home/opc/.hermes/hermes-agent/venv/bin/hermes <subcommand> \
          [args]
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Pitfalls
- Port conflicts (e.g. dashboard vs 9119): check with `sudo ss -ltnp | grep 9119` before enabling.
- SELinux enforcing on Oracle Linux prevents naive `/etc` edits via interactive editors; prefer `sudo tee` when patching unit files.
- Never silently swap backend stacks mid-flight.

### Workflow
1. `sudo tee` or `sudo vim` to edit unit, then `sudo systemctl daemon-reload`.
2. `sudo systemctl reset-failed <unit>` then `sudo systemctl restart <unit>`.
3. Use `journalctl -xeu <unit> -n 80` for the real failure cause.
4. Verify executable path runs for the target user before declaring success.

For deeper journalctl/systemctl recipes, see `references/systemd-debugging.md` (moved from `hermes-systemd-services`).
