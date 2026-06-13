---
name: hermes-platform-operations
description: "Platform lifecycle for Hermes installations: auto-backup strategy, systemd unit management, s6 container supervision, service exposure, and gateway ops. For any question about keeping a Hermes deployment alive, backed up, and reachable."
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [platform, ops, deployment, container, backup, systemd, s6, docker]
---

# Hermes Platform Operations

This umbrella consolidates the distinct platform-level concerns for running Hermes in production:
- systemd units (Oracle Linux, SELinux, unit authoring)
- s6-overlay supervision (Docker image architecture, per-profile gateways)
- auto-backup (cron-driven GitHub backups of `~/.hermes`)
- service exposure (Tailscale, SSH tunnels, reverse proxies, firewalls)

For messaging gateway troubleshooting on top of these surfaces, also load `gateway-ops`.

## Subsystems

### A. Systemd-hosted Hermes services

Use `gateway-ops` for the operational commands (`hermes status --all`, log triage, restart flows).
Use this section only for unit authoring and platform-level troubleshooting on Oracle Linux / SELinux.

Required unit shape:
- `Type=simple`, explicit `HOME`/`USER`/`WorkingDirectory`
- Run `python3 <venv>/bin/hermes <subcommand>` directly
- Log to journal

Pitfalls:
- Port conflict: `sudo ss -ltnp | grep <port>`
- SELinux enforcing: edit `/etc/systemd/system/*.service` with `sudo tee`
- `sudo systemctl reset-failed <unit>` before restart if stuck failed

### B. Docker / s6-overlay supervision

Use the reference notes in `references/hermes-s6-container-supervision.md` for:
- Architecture B (CMD as main program, per-profile gateways under `/run/service/`)
- `docker exec <c> /command/s6-svstat /run/service/gateway-<name>`
- Adding new static services to the s6-rc bundle
- Reconciler behavior (`container-boot.log`, profile `SOUL.md` requirement)

### C. Config auto-backup (GitHub)

Use the reference notes in `references/hermes-auto-backup.md` for:
- Backup script path: `~/.hermes/scripts/backup-github.sh`
- Safe exclusions: `state.db`, `*.lock`, `logs/`, `.env`, `.auth`, `__pycache__`, `.hermes_history`
- Cron contract: `hermes-config-backup`, typically `every 1h`, forever
- Preferred SSH remote: `git@github.com:<owner>/<repo>.git`

### D. Service exposure (fronting a local Hermes service)

Use `gateway-ops` for messaging platform bindings.
Use this section only when the goal is making a locally-bound service reachable outside the host.

A) Tailscale: bind service `0.0.0.0`, peer uses host Tailscale IP, optional firewall rule restricting to `100.64.0.0/10`.
B) SSH tunnel: keep service on `127.0.0.1`, `ssh -L <local_port>:localhost:<service_port> user@host`.
C) Reverse proxy: keep service on localhost, nginx/caddy exposes HTTPS/auth.

Applied example: Hermes dashboard on 9119
- Active compose file: `~/.hermes/hermes-agent/docker-compose.yml`
- Change dashboard command host to `0.0.0.0` for Tailscale access.
- Do not update only `./hermes-config/...` or `/tmp/hermes-config/...` copies.

### E. Operational environment notes

- Oracle Linux 9 aarch64, home dir `700/drwx------`
- nginx serves from `/usr/share/nginx/html/projects/<projectName>` owned by `nginx:nginx`
- Backend proxies may need `setsebool -P httpd_can_network_connect on`
- Stage2 hook chowns `$HERMES_HOME/profiles` to hermes on every boot