---
name: dotenv-relocation
description: Move .env / .env.* files between system directories and application project directories, repair ownership and permissions, and verify app compatibility.
---

# Dotenv Relocation

Use when moving `.env` or `env.*` files from system dirs (e.g. `/var/lib`, `/etc/<app>`) into an application's project directory.

## Steps

1. **Locate** — `sudo find / -maxdepth 6 -type f \( -name '.env' -o -name '.env.*' -o -name '*.env' \) 2>/dev/null | sort`
   - Use `sudo find`; some `/var/lib/<app>` dirs are `drwxr-x---` and invisible to a normal user find.
2. **Identify project** — match by app name or test paths like `/var/www/html/projects/<app>`, `/home/<user>/<app>`, `/opt/<app>`
3. **Move with care** — 
   - If crossing user boundaries, use `sudo mv`
   - After move, `sudo chown <service_user>:<service_user> <project>/.env` — the app’s runtime user (e.g. `www-data`, `ubuntu`) must be able to read it
4. **Repair systemd unit files** if the service uses `EnvironmentFile=` pointing at the old path:
   - `sudo sed -i 's|old_path|new_path|' /etc/systemd/system/<app>.service`
   - `sudo systemctl daemon-reload`
   - `sudo systemctl restart <app>.service`
   - `sudo systemctl is-active <app>.service` to confirm
5. **Verify** — `ls -la <project>/.env` shows correct owner/group
6. **Check for hardcoded references** — `grep -r 'old_path' <project> /opt/<app> /etc/<app>`
6. **Cleanup** — remove stale `.env.bak.*` files if confirmed no longer needed

## Pitfalls

- ``mv` across user dirs without sudo = Permission denied`. If this happens, `sudo mv` then chown.
- **Systemd `EnvironmentFile=` must be updated** — many Go services running under systemd read `.env` via `EnvironmentFile=/var/lib/<app>/.env`. After moving the file, the unit file must point to the new path, then `systemctl daemon-reload` and restart.
- **Service user ownership** — after moving, `chown` to the service runtime user from the unit file (`User=` line), not to the user who did the move.
- Apps with fallback paths (e.g. Go files enumerating `/.env`, `/var/lib/<app>/.env`) will still work, but the canonical path should be updated so the fallback becomes redundant.
- Some infrastructure stores `.env` under `/var/lib/<app>` because of data-path conventions; moving it into the code repo is usually safer but check if a systemd service file references the old path.

## References

- `references/relocation-checklist.md` — condensed checklist and common patterns
