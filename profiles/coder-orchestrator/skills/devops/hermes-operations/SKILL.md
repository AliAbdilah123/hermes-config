---
name: hermes-operations
description: "Use when operating Hermes itself after installation: configuring profile-aware services, gateway routing behavior, Discord threading/free-response delivery, systemd units, scheduled config backups, logs, runtime paths, and service verification on Linux hosts."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [hermes, operations, gateway, discord, systemd, backup, cron, profiles, troubleshooting]
    related_skills: [hermes-agent]
---

# Hermes Operations

## Overview

This umbrella covers operating Hermes Agent itself on a Linux host after it is installed: supervised services, profile-aware config paths, gateway routing/debugging, Discord thread behavior, logs, and scheduled backups of Hermes configuration.

Use this class-level skill instead of separate session-specific skills for a Hermes systemd unit, Discord gateway routing explanation, or automatic config backup script.

## When to Use

Use when the user asks to:
- Run Hermes dashboard/gateway/worker as a systemd service.
- Debug why a Hermes systemd unit failed, restarted, or bound the wrong port.
- Explain why a Discord message was handled in a channel vs thread, or why auto-threading/free-response behavior differed from expectation.
- Inspect Hermes gateway logs, active profile config, and reply target routing.
- Back up Hermes profile/config/skills/plugins/memories to Git on a schedule.
- Create or audit a Hermes cron job that runs a fixed maintenance action.

If the task is about installing, configuring, or changing Hermes Agent itself, also load `hermes-agent` for current CLI/config commands.

## Profile and Path First Principles

- Identify the active profile before editing files. Runtime config usually lives under `~/.hermes/profiles/<profile>/config.yaml`; root `~/.hermes/config.yaml` may belong to another profile/session.
- Logs usually live under the active profile’s `logs/` directory.
- Do not write another profile’s skills/plugins/cron/memories unless the user explicitly directed that profile.
- For systemd, set `HOME`, `USER`, and `WorkingDirectory` explicitly so Hermes resolves the intended profile/config.

## Systemd Services for Hermes Components

Use a simple unit shape:

```ini
[Unit]
Description=Hermes <component>
After=network.target

[Service]
Type=simple
User=<user>
Group=<group>
Environment=HOME=/home/<user>
Environment=USER=<user>
WorkingDirectory=/home/<user>
ExecStart=/home/<user>/.hermes/hermes-agent/venv/bin/python3 /home/<user>/.hermes/hermes-agent/venv/bin/hermes <subcommand> [args]
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Workflow:
1. Check port conflicts first with `sudo ss -ltnp | grep <port>`.
2. Write/edit unit with `sudo tee` when under `/etc/systemd/system/`.
3. `sudo systemctl daemon-reload`.
4. `sudo systemctl reset-failed <unit>` and restart.
5. Read `journalctl -xeu <unit> -n 80 --no-pager` for real failure cause.
6. Verify command as the target user before blaming systemd.

Reference: `references/hermes-systemd-services-legacy.md` and `references/hermes-systemd-services-systemd-debugging.md`.

## Discord Gateway Routing and Thread Behavior

Workflow:
1. Inspect effective `discord:` config for `require_mention`, `thread_require_mention`, `free_response_channels`, `allowed_channels`, `ignored_channels`, `no_thread_channels`, `auto_thread`, and `history_backfill`.
2. Read gateway logs for `inbound message`, `response ready`, and `Sending response`; compare parent channel ID vs thread ID.
3. Explain behavior using adapter conditions, not guesses.
4. Remember that free-response channels, no-thread channels, voice-linked channels, and Discord reply messages can bypass auto-thread creation even when `auto_thread: true`.

Reference: `references/discord-gateway-routing-legacy.md` and `references/discord-gateway-routing-auto-thread-free-response.md`.

## Hermes Config Backups

Use when the user wants periodic Git/GitHub backups of Hermes config.

Workflow:
1. Choose or verify backup repo/remote.
2. Prepare a clean staging repo under a backup path such as `~/.hermes-backups/`.
3. Use an idempotent backup script that excludes runtime/state/secrets.
4. Run once manually and verify commit/push status.
5. Create a Hermes cron job for recurring execution.
6. Report changed file count, commit hash or “No changes to commit”, and push status.

Do not push by default:
- SQLite runtime state (`state.db*`), locks, pids, logs.
- `.env`, `.auth`, credentials, node_modules, caches, pyc files.
- History/snapshot files that are runtime implementation detail.

Script reference: `scripts/hermes-auto-backup-backup-github.sh`.
Legacy notes: `references/hermes-auto-backup-legacy.md`.

## Common Pitfalls

- Editing the wrong profile because root `~/.hermes/` and `~/.hermes/profiles/<profile>/` are both present.
- Trusting `systemctl status` without reading the journal.
- Starting a second dashboard/gateway process when a port is already bound.
- Claiming Discord cannot thread when config/code conditions show threading was suppressed by channel state.
- Backing up secrets or runtime DB files to Git.
- Forgetting that cron-run sessions have no current chat context; prompts must be self-contained.

## Verification Checklist

- [ ] Active profile and config path confirmed.
- [ ] Logs inspected from the active profile or journal as appropriate.
- [ ] Service command verified as the target user.
- [ ] Ports/listeners checked after restart.
- [ ] Gateway routing explanation cites the exact config/log condition.
- [ ] Backup script run once manually before scheduling.
- [ ] Cron job listed after creation/update.
