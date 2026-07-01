# Observed user-unit pitfalls

## `Group=` -> exit 216/GROUP

- Symptom: `9router.service: Failed to determine supplementary groups: Operation not permitted` + `status=216/GROUP`, repeated restart loop.
- Cause: user-level systemd managers typically run without the privilege to alter group lists. `Group=` is silently rejected in most user units.
- Fix: remove the `Group=` line. The service already runs as `User=ubuntu` and inherits that user's primary group (and any supplementary groups already granted at PAM login). If you truly need additional supplementary groups, grant them through PAM/logind (e.g., add the user to extra groups and use `loginctl enable-linger <user>`; do not rely on `Group=` inside the unit).

## Blog post structure (for future reference)

- Linger check before assuming a user service is broken: `loginctl show-user <user> | grep -i linger`.
- Reproduce the failure mode with `sudo -u <user> env -i HOME=/home/<user> PATH=... /path/to/binary` to simulate the stripped env systemd will present.

## COMMAND policy

- For `node` CLIs installed globally (e.g. `/home/ubuntu/.local/bin/9router`), always test the exec path before dropping it into the unit:
  ```bash
  sudo -u ubuntu HOME=/home/ubuntu PATH=/home/ubuntu/.local/bin:/usr/local/sbin:/usr/bin:/bin /home/ubuntu/.local/bin/9router --skip-update -p 20128 --no-browser
  ```
- For headless services, inspect `--help` and pass all UX flags that would otherwise open browsers/trays in interactive mode. Don’t guess flags.

## Proven structure

- `StartLimitIntervalSec=0` during active debugging to prevent the 5-retry-per-30s cutoff.
- `Restart=always` for routers/proxies. `on-failure` for batch jobs.
- `KillMode=mixed` + `KillSignal=SIGTERM` + `TimeoutStopSec=210` to match graceful shutdown expectations while still killing stragglers.

## `User=` in user units -> exit 216/GROUP

- Symptom: `server-monitor.service: Failed to determine supplementary groups: Operation not permitted` + `status=216/GROUP`, repeated restart loop.
- Cause: the user manager already runs as the owning user. Adding `User=` triggers a redundant group-resolution step that fails without elevated privileges.
- Fix: remove the `User=` line entirely from `~/.config/systemd/user/*.service`.

## Tested service recipe (Go binary)

```ini
[Unit]
Description=Server Monitor
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/ubuntu/projects/server-monitor/backend
ExecStart=/home/ubuntu/projects/server-monitor/backend/server
Environment=PORT=8081
Restart=on-failure
RestartSec=3

[Install]
WantedBy=default.target
```

Notes:
- No `User=` line.
- Use absolute paths for `ExecStart` and `WorkingDirectory`.
- Reload with `systemctl --user daemon-reload` after edits.
