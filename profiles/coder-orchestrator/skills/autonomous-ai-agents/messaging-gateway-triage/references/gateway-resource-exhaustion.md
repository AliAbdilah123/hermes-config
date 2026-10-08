# Gateway non-response caused by host resource exhaustion

Use this when a messaging gateway process is still `active (running)` but stopped receiving or sending messages.

## Evidence pattern

Correlate gateway and kernel logs over the same bounded time window:

```bash
journalctl --user -u hermes-gateway.service --since '12 hours ago' --no-pager
journalctl -k --since '12 hours ago' --no-pager | grep -Ei 'oom|out of memory|killed process'
free -h
swapon --show
systemctl --user show hermes-gateway.service \
  -p MainPID -p NRestarts -p MemoryCurrent -p MemoryPeak
```

A strong diagnosis is:

- kernel reports exhausted RAM/swap and repeated OOM kills;
- platform adapter reports stale ACKs, blocked heartbeats, socket closure, or reconnect failure at matching timestamps;
- gateway remains active with no later inbound/send events.

This is a live-but-stalled transport, not proof that routing or nginx failed.

## Attribute memory correctly

`systemctl status` reports the service cgroup, including tool descendants. Compare it with the gateway process RSS:

```bash
ps -o pid,ppid,rss,etimes,args -p "$(systemctl --user show -p MainPID --value hermes-gateway.service)"
systemctl --user status hermes-gateway.service --no-pager
```

Large differences usually come from inherited Chromium, language-server, preview-server, or capture processes. Do not describe the whole cgroup as Python/gateway memory.

## Session-count distinction

A conversation idle reset and stored-session retention are separate controls:

- `session_reset.mode: idle` with `idle_minutes` starts a fresh conversation after inactivity.
- `sessions.auto_prune: true` with `retention_days` deletes old database records.

An `idle_minutes` value does nothing when reset mode is `none`; resetting conversations does not prune history. Check the effective config for every running profile.

## Recovery and prevention

1. Preserve evidence before cleanup.
2. Terminate demonstrably stale browser/LSP process trees; avoid killing active work solely by process name.
3. Restart the affected gateway from an external shell. A gateway child command may be unable to restart its own parent because systemd/cgroup termination kills the command mid-operation.
4. Bound the gateway cgroup with `MemoryHigh`, `MemoryMax`, and `MemorySwapMax`, accounting for legitimate child-tool workload.
5. Add bounded cleanup for abandoned browser/LSP roots and verify it twice: first run removes stale trees; second run removes nothing.
6. Alert on **available RAM** and **swap utilization**, with hysteresis/deduplication. Used-RAM percentage alone misses swap exhaustion.
7. Add swap only as secondary protection; it does not replace cleanup and cgroup limits.
8. Verify platform reconnection/inbound delivery, current resources, timers, and any public services potentially affected.

## Chromium accounting pitfall

`pgrep -af 'chrom(e|ium)'` can count zombies and the matching probe itself. Report live and zombie processes separately using process state. Chromium normally has several child processes per browser; count browser roots/profile directories as well as raw PIDs.

## Safety

- Do not store messaging tokens in newly written monitoring scripts. Reuse an existing protected credential source or Hermes delivery mechanism.
- Do not claim a restart succeeded from an empty chained command result. Read back PID/start time and inspect fresh logs.
- Do not infer that a configured 24-hour timeout means pruning is enabled; inspect both reset and retention settings.
