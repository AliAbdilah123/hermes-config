Hermes-specific systemd debugging notes (Oracle Linux 9, SELinux enforcing)

Quick diagnostic path
1. `sudo systemctl status <unit> --no-pager` -> active / auto-restart / exit status
2. `sudo systemctl reset-failed <unit>` before restart if it is stuck Failed
3. `sudo journalctl -xeu <unit> -n 200` -> real cause, not status shorthand
4. `sudo ss -ltnp | grep <port>` -> what is already listening
5. `sudo pgrep -af 'hermes .* <subcommand>'` -> stray processes outside systemd

Common failure signatures
- status 203/EXEC + Permission denied
  -> Executable or some parent directory is blocked for the runtime user.
  -> Prefer `python3 <venv>/bin/hermes ...` over the wrapper script.
  -> Ensure `HOME`, `USER`, and `WorkingDirectory` are set.
- status 1/FAILURE + address already in use
  -> Port 9119 collision with another dashboard. Stop the other service or choose a
     distinct port.
- Interactive auth required from `systemctl`
  -> Prefix the command with one `sudo`, then run edit/reload/start in one line.

SELinux note
In `Enforcing` mode, `/etc/systemd/system/*.service` is managed via `sudo tee`; a
missing `Environment=HOME=/home/opc` can cause config lookups under `/` instead of the
user's profile home. If that still fails, temporarily `sudo setenforce 0` to confirm
SELinux is the cause, then either fix the unit envs or add a targeted policy change.

The user's environment
- Oracle Linux 9 aarch64, nginx 1.20.1, home dir 700/drwx------
- Active Hermes profile: default
- Public route currently: http://168.110.196.49/projects/<projectName>
- nginx serves from `/usr/share/nginx/html/projects/<projectName>` owned by `nginx:nginx`
- Gateway setting often required for backend: `setsebool -P httpd_can_network_connect on`

Reference commands
- `sudo ss -ltnp | grep 9119`
- `sudo systemctl daemon-reload`
- `sudo systemctl reset-failed hermes-dashboard.service`
- `sudo systemctl restart hermes-dashboard.service`
- `sudo -u opc bash -lc '/home/opc/.hermes/hermes-agent/venv/bin/python3 ...'`
