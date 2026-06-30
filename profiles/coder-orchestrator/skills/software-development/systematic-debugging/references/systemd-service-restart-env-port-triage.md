# Systemd Service Restart / Env-Port Triage

Use this when a user says they updated `.env` and asks to restart a Linux service, especially for web/API apps managed by `systemd`.

## Checklist

1. Identify the actual service unit and how it loads environment:
   ```bash
   systemctl list-units --type=service --all | grep -i '<project>'
   sudo systemctl cat <service>.service
   ```
   Look for `WorkingDirectory=`, `EnvironmentFile=`, and `ExecStart=`. Do not assume the edited `.env` file is the one systemd reads.

2. Restart and immediately verify the unit state:
   ```bash
   sudo systemctl restart <service>.service
   systemctl is-active <service>.service
   systemctl status <service>.service --no-pager -l
   ```
   A service can briefly report started and then enter `activating (auto-restart)` / failed.

3. If it fails, read fresh logs before making changes:
   ```bash
   journalctl -u <service>.service -n 80 --no-pager -l
   ```

4. For `bind: address already in use`, inspect the live listener and compare with the intended port/address:
   ```bash
   sudo ss -ltnp | grep ':<port>'
   ```
   Then inspect the app's env names in code if needed (`ADDR`, `PORT`, `HOST`, etc.).

5. Fix the environment source, not just the running shell. If the app expects `ADDR=:8089` and systemd reads `/path/project/.env`, put the value there, then restart again.

6. Verify after restart with both process state and listener state:
   ```bash
   systemctl is-active <service>.service
   systemctl status <service>.service --no-pager -l
   sudo ss -ltnp | grep ':<expected-port>'
   curl -i --max-time 10 http://127.0.0.1:<expected-port>/...
   ```

## Pitfalls

- A root/project `.env` may differ from an app-level `.env`; systemd only reads the file named in `EnvironmentFile=`.
- `systemctl restart` can return successfully even when the process exits seconds later and is in an auto-restart loop.
- `PORT=8089` may not matter if the application code reads `ADDR` or another variable name.
- Do not kill the process occupying the conflicting port until you identify it; it may be another production service.
