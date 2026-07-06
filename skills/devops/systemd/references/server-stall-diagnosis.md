# Systemd ops references: watchdogs, health probes, and shell gotchas

## Server-stall diagnosis: summarize from a freeze event

When asked "why didn't the server respond / SSH die", these journal signatures are the
most informative (filenames will match `NO_PAGER` or actual journald output):

| Window | What to grep | What it means |
|---|---|---|
| 2h before freeze | `sshd: kex_exchange_identification: read: Connection reset by peer` | TCP/net stack already under stress; inbound SSH starts dropping |
| 0–2h before freeze | `unified-monitoring-agent … fluentd config … is empty, no need to restart fluentd as it is expected to be hung` (repeated) | Oracle agent reports its own monitor daemon stuck; system degraded but not dead |
| At freeze | `snapd.service: Watchdog timeout` | systemd watchdog fired; service loop was unresponsive for >5 min |
| At freeze | `systemd-journald.service: Watchdog timeout` | journald itself froze — strong evidence of a system-wide soft lockup, not a single-process OOM |
| Absent when lockup | `oom-killer`, `killed process`, `Out of memory` | Rules out classic OOM as the root cause |

**Absence of OOM + presence of multiple watchdog fires + load average climbing** = most likely
a CPU or I/O stall (e.g. Hermes agent + browser automation + Chromium snap + many Go APIs
racing while snapd adjusts profiles). A write-test probe (`touch /tmp/.watchdog_test`) that
times out is the filesystem/MMAP equivalent of the same stall.

## Bash health-check script pitfalls (observed on this host under bash 5.2 / `set -euo pipefail`)

1. **`awk` ternary in `[` test**: `awk 'BEGIN{print (l>n)?1:0}'` works in isolation but bash
   can parse the `)` as unexpected when embedded directly in `[ "$(awk ...)" -eq 1 ]`. Safer:
   ```bash
   LOAD_OK=$(awk -v l="$LOAD" -v n="$NPROC" 'BEGIN{if(l>n) print 1; else print 0}')
   if [ "$LOAD_OK" -eq 1 ]; then ...; fi
   ```

2. **`df` inside command substitution**: `awk 'NR==2{...}' "$(df /)"` fails because `$(df /)`
   produces multi-line text, which bash tries to open as a filename. Correct forms:
   ```bash
   df / | awk 'NR==2{...}'
   # or
   read -r DISK_PCT < <(df / | awk 'NR==2{...}')
   ```

3. **Unit name mismatch for SSH**: On Ubuntu 24.04, the systemd unit is `ssh.service` (not `sshd.service`).
   `systemctl is-active sshd` returns inactive; use `systemctl is-active ssh`.

4. **Alerts log path**: Always prefer `$HOME/watchdog-alerts.log` (no `sudo` needed).
   `/var/log/watchdog-alerts.log` causes permission-denied from cron user jobs.

5. **`crontab` not installed**: Minimal containers/VPS images may lack `cron` package entirely.
   Install with `sudo apt-get install -y cron` and enable `cron.service`.

## Cron + flock single-instance pattern

```bash
LOCKFILE="/tmp/watchdog.lock"
exec 200>"$LOCKFILE"
flock -n 200 || exit 0
```
Placed at the top of a cron script, this guarantees one instance at a time and silently exits
if a previous run is still active. Useful for any short probe that shouldn't stack.

## When to use an external monitor vs this in-server probe

- In-server probe (`*/2 * * * *`) catches: service down, load spikes, low memory, disk saturation, write-test hangs.
- Cannot catch: complete network loss, hypervisor/host-level block, CRIU/migration freeze.
- Pair with an **external HTTP health monitor** (UptimeRobot / Kuma / Oracle Monitoring alarm on
  `http://<host>/` or a `/healthz.html` static path) to catch full drop.
- A static `healthz.html` under the nginx document root is the cheapest external probe target:
  ```bash
  echo "ok" | sudo tee /usr/share/nginx/html/healthz.html
  ```

## Systemd WatchdogConfig (proactive, not reactive)

Adding `WatchdogSec=30` (or similar) to a service's unit file causes systemd to auto-restart the
service if its main loop doesn't call `sd_notify("WATCHDOG=1")` within the window. This turns
silent hangs into automatic recovery, often faster than a human-driven probe cycle. If the
application is a simple Go HTTP server that doesn't support sd_notify, set `WatchdogSec=0` (off)
and rely on the external HTTP health probe + systemd `Restart=always`.
