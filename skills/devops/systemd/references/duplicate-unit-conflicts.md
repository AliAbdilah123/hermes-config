# Duplicate service instances: the SIGKILL death spiral

## Symptom

A long-running service dies every 60–150s with **no error of its own**, then systemd restarts it:

```
9router.service: Main process exited, code=killed, status=9/KILL
9router.service: Failed with result 'signal'.
9router.service: Scheduled restart job, restart counter is at 24.
```

Downstream clients see connection failures that come and go (`APIConnectionError`, HTTP 502/503,
empty responses) because the listener is yanked mid-request. `NRestarts` climbs into the dozens.

## Key insight: `status=9/KILL` is a deliberate kill, not a crash or OOM

- `status=9/KILL` / `Failed with result 'signal'` = someone sent SIGKILL.
- An app crash is `status=1/FAILURE`, `status=11/SEGV`, `status=6/ABRT`.
- **OOM would show** `Out of memory: Killed process` / `oom-kill` in `dmesg -T` and
  `journalctl -k`. Absence of those + no `systemd-oomd` entries rules OOM out.
- No coredump, no stack trace, no app log line before death = external killer. Look for it.

## Root cause pattern: two units owning the same service

A service can be legitimately installed **twice at once** with the same name:

| Scope | Unit file | Managed by | Journal |
|---|---|---|---|
| system | `/etc/systemd/system/<n>.service` | `systemctl` | `sudo journalctl -u <n>` |
| user | `~/.config/systemd/user/<n>.service` | `systemctl --user` | `journalctl --user -u <n>` |

These are **separate units in separate managers** — neither shadows the other, and both can be
`enabled` + `active` simultaneously. `systemctl status <n>` from an interactive shell shows the
*system* one; `systemctl --user status <n>` shows the *user* one. Checking only one hides half
the evidence.

If the app **reaps whatever owns its port on startup** (many Node/CLI daemons do — e.g. 9router's
CLI calls `killAllAppProcesses(port)` then `killProcessOnPort(port)` before binding), the two
copies enter a kill loop:

```
instance A starts -> SIGKILLs B (owns port) -> B's unit restarts -> SIGKILLs A -> ...
```

Each restarted copy kills the other. Forever. Neither logs an error; both look "healthy" apart
from the kill.

## Diagnosis

```bash
# 1. Are there TWO units with this name?
systemctl is-active  <n>; systemctl is-enabled  <n>     # system scope
systemctl --user is-active <n>; systemctl --user is-enabled <n>  # user scope
systemctl cat <n>; systemctl --user cat <n>              # compare ExecStart

# 2. Read BOTH journals around one kill. They do not interleave.
sudo journalctl -u <n>.service --since "<k-2min>" --until "<k+2min>" --no-pager
journalctl --user -u <n>.service --since "<k-2min>" --until "<k+2min>" --no-pager

# 3. Rule out OOM explicitly
sudo dmesg -T | grep -iE "out of memory|oom-kill|Killed process"
journalctl --user -u systemd-oomd --since "1 hour ago" --no-pager

# 4. Who owns the port right now, and what is its parent?
ss -ltnp | grep <port>
ps -eo pid,ppid,etime,args | grep "[<app>]"
```

Cgroup parent tells you the owner at a glance:
`/system.slice/<n>.service` = system unit; `/user.slice/user-<uid>.slice/.../<n>.service` = user unit.

## Fix

Pick **one** owner and disable the other. Prefer the unit that holds app state and runs
unprivileged (usually the user unit if the data dir is under `$HOME`):

```bash
sudo systemctl disable --now <n>.service     # removes multi-user.target.wants symlink
systemctl --user restart <n>.service
```

Disabling is enough — do **not** delete the file. Leaving it documents the conflict and makes
the diagnosis reproducible. Re-verify:

```bash
systemctl is-active  <n>   # expect inactive
systemctl is-enabled <n>   # expect disabled
systemctl --user show <n> -p ActiveEnterTimestamp -p NRestarts   # timestamp should stop moving
journalctl --user -u <n>.service --since "<fix time>" | grep -c 'status=9/KILL'   # expect 0
```

Watch for ≥3 minutes (longer than the observed restart period) before declaring it fixed; the
kill loop's period IS the restart interval, so a single quiet minute proves nothing.

## Case study (2026-09-12, this host)

`/etc/systemd/system/9router.service` was created at 21:52 while
`~/.config/systemd/user/9router.service` had been serving since June. Both enabled, both
running `9router` on port 20128. 71 restarts in ~80 minutes; the user unit accumulated 27.

```
21:55:08 user:   status=9/KILL          <- killed by the system copy
21:55:13 user:   Scheduled restart job, restart counter is at 1
21:57:12 user:   status=9/KILL          <- repeat
...
hermes-gateway: APIConnectionError ... base_url=http://127.0.0.1:20128/v1
```

Cause of the SIGKILL: 9router's own CLI, on every startup, runs
`killAllAppProcesses(port)` + `killProcessOnPort(port)` and SIGKILLs the current port owner.
The other copy's systemd `Restart=always` immediately revived it, which killed the first. Note
the port-owner kill was fired by the *app*, so nothing in either unit file looks wrong.

An earlier hypothesis — `localhost` resolving to `::1` while the router binds IPv4 — was
**tested and disproven** on this host: `getent ahosts localhost` returned `127.0.0.1` only,
`http://localhost:20128` succeeded, and only literal `http://[::1]:20128` was refused. When a
client and a router share a host and calls intermittently fail, check for duplicate instances
before blaming name resolution.
