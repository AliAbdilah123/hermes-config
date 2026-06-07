# Legacy skill package: `hermes-systemd-services`

This file preserves the former `hermes-systemd-services` SKILL.md after consolidation into `hermes-operations`. Relative support-file links have been rewritten to the re-homed files under `hermes-operations`.

---

---
name: hermes-systemd-services
title: Hermes systemd services
description: Manage Hermes components as systemd services on Oracle Linux with SELinux enforcing. Covers unit file structure, environment, common failure modes, port conflicts, and verification steps.
triggers:
  - systemd unit for hermes
  - hermes-dashboard.service
  - hermes gateway service
  - sudo systemctl daemon-reload hermes
  - permission denied systemd hermes
---

# Hermes systemd services

Use this skill whenever creating, repairing, or debugging a systemd unit that runs any
Hermes component (dashboard, gateway, worker) as a managed service.

## Required unit shape

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

Why these choices:
- `Type=simple` + explicit envs make the process find `~/.hermes` config.
- Run `python3` directly, not the wrapper script, to avoid permission edge cases.
- Log to journal so `journalctl -xeu` gives you the real failure trace.

## Pitfalls

- Port conflicts: another `hermes dashboard` may already be bound to 9119.
  Check with `sudo ss -ltnp | grep 9119` before enabling another unit.
- SELinux enforcing in Oracle Linux will break a naive writable `/etc` patch flow:
  use `sudo tee` for `/etc/systemd/system/*.service` edits.
- Never switch stacks mid-flight without explicit user approval.
- Do not silently swap Go/Python/TS/React stacks after the user has chosen one.
  Once the user has confirmed TS/React + Go + SQLite, do not replace the backend or
  frontend without explicit approval.

## Workflow

1. Edit unit with `sudo tee` if needed; reload with `sudo systemctl daemon-reload`.
2. Reset failed state before restart:
   `sudo systemctl reset-failed <unit>` then `sudo systemctl restart <unit>`.
3. Read the actual cause from `journalctl -xeu <unit> -n 80`, not just status.
4. If auth prompts block you, sudo once for the whole edit/reload/start sequence.
5. Verify executable path works for the target user first:
   `sudo -u opc bash -lc '/home/opc/.hermes/hermes-agent/venv/bin/python3 /home/opc/.hermes/hermes-agent/venv/bin/hermes <cmd>'`.
6. Confirm the port with `sudo ss -ltnp | grep <port>` after `status` shows active.

## Support files

See `references/hermes-systemd-services-systemd-debugging.md` for concrete `journalctl` and `systemctl` recipes.
