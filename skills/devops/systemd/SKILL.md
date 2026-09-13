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
   - **No `User=` and no `Group=` in a user-level unit.** Both trigger `status=216/GROUP` — see Pitfalls.
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

## Diagnosing a service that keeps dying

Check the **exit status code** before anything else — it names the class of fault:

| Code | Meaning |
|---|---|
| `status=9/KILL`, `Failed with result 'signal'` | Something SIGKILLed it. **External**, not a crash. |
| `status=1/FAILURE` | The app itself exited non-zero — read its own logs. |
| `status=11/SEGV`, `status=6/ABRT` | App crash; look for a coredump. |
| `status=216/GROUP` | `User=`/`Group=` in a user unit. See Pitfalls. |

Then, for `9/KILL`: find the killer. A host can legitimately have the **same service name
installed twice** — `/etc/systemd/system/<n>.service` (system scope) and
`~/.config/systemd/user/<n>.service` (user scope) are separate units in separate managers, and
both can be enabled and running. Apps that reap whatever owns their port on startup then trade
SIGKILLs forever. **Always check both scopes before concluding anything:**

```bash
systemctl is-active <n>; systemctl --user is-active <n>   # both, not one
systemctl cat <n>;       systemctl --user cat <n>          # compare ExecStart
```

Also rule OOM out explicitly (absence of `dmesg`/`journalctl -k` OOM lines is a finding, not a
gap). Full procedure, cgroup-owner trick, fix, and a worked case study:
`references/duplicate-unit-conflicts.md`.

**Observation window for restart loops:** the loop's period *is* the restart interval. A single
quiet minute proves nothing — watch ≥3× the observed interval (check `NRestarts` and
`ActiveEnterTimestamp` for movement) before declaring a fix.

## Pitfalls

- **`Group=` in user units causes `Failed with result 'exit-code' status=216/GROUP`.** Remove it; user unit runs as `User=` and inherits that user's primary group.
- **`User=` in a user-level unit also triggers `status=216/GROUP` ("Failed to determine supplementary groups").** Remove the `User=` line entirely; a user manager already runs as the owning user and cannot re-resolve supplementary groups.
- **TTY/dbus issues:** Tray/OSC apps may misbehave under `Type=notify` or without a session bus. Prefer `--no-tray`/`--headless` under systemd.
- **Env drift:** don’t inherit a shell env blindly. Set only what the service needs (`PATH`, `HOME`, app vars) and use absolute paths for everything.
- **Double activation:** if you’re replacing a manual foreground launch, ensure the old PID exits before `start`-ing the unit, or the bind will fail.
- **Same-name unit installed at both scopes.** A system unit and a user unit with the same filename do **not** shadow each other; both can be enabled and active. If the app reaps its own port on startup, they SIGKILL each other in a loop (`status=9/KILL` every restart interval). Check `systemctl is-active <n>` AND `systemctl --user is-active <n>` together — inspecting one scope hides the culprit.
- **`systemctl --user` needs `XDG_RUNTIME_DIR`.** In cron jobs, `sudo`, `env -i`, or any shell without a session, `systemctl --user` fails with `Failed to connect to bus: No medium found` — the `2>/dev/null` in a health check swallows that and reports a **false "service down"**. Export it first:
  ```bash
  export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
  ```
  Verify any such script under a stripped environment, not from your interactive shell:
  ```bash
  env -i HOME=$HOME PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin bash ./health-check.sh
  ```

- `references/user-unit-pitfalls.md` — tested failure modes and environment recipe for user-level units (e.g. `status=216/GROUP` when `Group=` is set, how to reproduce with stripped env, command-policy guidance).
- `references/server-stall-diagnosis.md` — diagnosing server freezes from journal signatures, bash health-check script pitfalls, `ssh` vs `sshd` unit-name mismatch, cron + flock single-instance pattern, and watchdog timeout semantics.
- `references/duplicate-unit-conflicts.md` — `status=9/KILL` triage, same-name units at system *and* user scope fighting over one port, cgroup-owner identification, fix + verification, and a worked case study.
- `references/code-server-config-gotcha.md` — `default:` is not a valid code-server config key; to open a directory on startup, pass it as a CLI argument in `ExecStart` instead of `default:` in `config.yaml`.
- `references/code-server-blank-page.md` — blank/unreachable code-server checklist: UFW allow for the bind port, CGNAT-range nft drops, login-page-vs-blank distinction, and confirmation commands.
- `templates/9router.service` — known-good user unit for the Node `9router` CLI (port 20128, headless, auto-restart).
- `templates/code-server.service` — known-good user unit for code-server that opens `/home/ubuntu` on port `8999` with password auth.