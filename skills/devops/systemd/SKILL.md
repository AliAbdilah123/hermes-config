---
name: systemd
description: Design, place, enable, and operate user-level systemd units on Linux hosts. Covers unit structure, environment/WorkingDirectory, restart policy, reload flow, and headless/graphical app gotchas.
tags:
  - linux
  - ops
  - services
---

# Systemd user services

Use when the user wants to "create a systemd service", "run X as a service", or manage long-lived background tasks under a non-root user.

## Locations

- Unit files: `~/.config/systemd/user/<service>.service`
- Symlinks for enable: `~/.config/systemd/user/default.target.wants/`
- Linger must be enabled for the user for services to survive logout: `loginctl enable-linger <user>`

## Create the unit

1. Write a `.service` file under `~/.config/systemd/user/`.
2. Key fields (see `templates/9router.service` for a real example):
   - `Type=simple` for foreground processes that don’t fork.
   - `User=` only. **Do not** put `Group=` in a user-level unit unless you know the manager has been explicitly authorized to set groups; the user manager commonly exits with status 216/GROUP on `Group=`.
   - `ExecStart=` must use an **absolute path** to the binary/script, and all flags that must not prompt (e.g. `--no-browser`, `--skip-update`, `--headless`).
   - `Environment="PATH=..."`
   - `Environment="HOME=..."` only if the app needs a reliable HOME and `Environment=` doesn’t already set it.
   - `WorkingDirectory=` to the app’s data root (e.g. `~/.<app>`).
   - `Restart=always` for daemons, or `on-failure` when only transient failures should trigger restart.
   - `RestartSec=5`
   - `KillMode=mixed` with `KillSignal=SIGTERM` (matches daemon behavior where main must exit cleanly but children can be SIGKILLed).
   - `TimeoutStopSec=210` for apps that take long to shut down.
   - `StandardOutput=journal` and `StandardError=journal`.
   - Optionally `StartLimitIntervalSec=0` while debugging to avoid rate-limiting rapid retries.

3. Reload + enable + start:
   ```bash
   systemctl --user daemon-reload
   systemctl --user enable <service>.service
   systemctl --user start <service>.service
   ```

4. Verify with `systemctl --user status <service>`, `ss -tlnp`, `journalctl --user -u <service> --no-pager -n 50`.

## Patching + restarting

- Edit the unit, then: `daemon-reload` → `restart <service>`.
- If `restart` appears to hang (especially after a SIGTERM-sensitive service): `Systemctl --user stop <service>; kill -9 <oldPID> if needed; systemctl --user start <service>`.
- If restart loops after a bad unit, fix the unit first, or stop the service before patching to avoid noisy journal spam.

## App-specific flags for headless

- GUI/tray apps launched by systemd: pass the app’s equivalent of `--no-browser` / `--headless` / `--no-tray`. Inspect `--help`; don’t guess.
- For Node apps: put `node_modules/.bin` and app dir in `PATH`, or use `NODE_PATH` if the app expects it.

## Pitfalls

- **`Group=` in user units causes `Failed with result 'exit-code' status=216/GROUP`.** Remove it; user unit runs as `User=` and inherits that user’s primary group.
- **TTY/dbus issues:** Tray/OSC apps may misbehave under `Type=notify` or without a session bus. Prefer `--no-tray`/`--headless` under systemd.
- **Env drift:** don’t inherit a shell env blindly. Set only what the service needs (`PATH`, `HOME`, app vars) and use absolute paths for everything.
- **Double activation:** if you’re replacing a manual foreground launch, ensure the old PID exits before `start`-ing the unit, or the bind will fail.

- `references/user-unit-pitfalls.md` — tested failure modes and environment recipe for user-level units (e.g. `status=216/GROUP` when `Group=` is set, how to reproduce with stripped env, command-policy guidance).
- `templates/9router.service` — known-good user unit for the Node `9router` CLI (port 20128, headless, auto-restart).