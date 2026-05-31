---
name: service-exposure-debugging
description: "Service unreachable/broken exposure debugging: ports, firewalls, SELinux, nginx, Tailscale, localhost-only loopback aliases, proxy-ready paths, and restart loops."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [debugging, networking, linux, tailscale, selinux, iptables, nginx, port-forwarding]
---

# Service Exposure Debugging

## When to Use
- A port-bound process answers `ss`/`netstat` but `curl` times out from the same host.
- A service was working and became unreachable with no obvious application change.
- Dashboard or app bindings visually show `0.0.0.0:<port>` but every probe hangs.
- Nginx path-based exposure (`/projects/<name>`) is needed, or a plain-port mapping stopped working.
- Services only work over Tailscale/tailscale0 but not locally.
- Repeated dashboard restart attempts keep crashing on SIGTERM/SIGUSR1 hints during readiness probes.

## Quick Reference
```
Connection reset on connect                 -> listener not accepting (backlog full / deadlocked accept loop) 
Timeout after TCP handshake                 -> application is stuck during/after handshake
Firewall has DROP rules for port except <if> -> explicit port-wide block
SELinux allows some things but blocks others -> AVCs in audit.log; permissive mode may hide real denials
Service won't survive background restart     -> needs supervised start or detached session
```

## 4-Phase Probe

### Phase 1 — Is the kernel actually listening?
- `ss -tlnp | grep <port>` / `ss -s state syn-recv`
- Expect `0.0.0.0:<port>` and no SYN-RECV pileup.
- If backlog fills instantly (many SYN-RECV), process is deadlocked in accept, not a firewall issue.

### Phase 2 — Is the loopback route valid?
- `ip route get <IP>`
- `lo` should own 127.0.0.1 and any 100.x/10 Tailscale-style loopback aliases.
- If `dev lo` is missing for 127.0.0.1, the loopback interface problem is the actual cause.

### Phase 3 — Is the process accepting?
- Raw socket connect test:
```python
import socket
s = socket.socket(); s.settimeout(2)
s.connect(('127.0.0.1', PORT)); print('ok'); s.close()
```
- Compare `127.0.0.1` vs actual local IP.
- If both timeout but `ss` says LISTEN, accept-loop bug confirmed.

### Phase 4 — Compare inbound firewall vs outbound connectivity
- `iptables-save` snapshot once so diffs are visible.
- A common failure mode: port-wide DROP with `-i tailscale0` ACCEPT exceptions.
  Locally-generated traffic does not arrive on tailscale0 → local curl fails.
  A curl via proxy may succeed because proxy uses `tailscale0`.

## Remediation Playbook

### A) Dashboard/agent listen deadlock
1. Kill old process: `kill <pid>`.
2. Restart with a detached session, do not use shell background:
```bash
terminal(background=True, notify_on_complete=True)
command="/home/opc/.hermes/.../venv/bin/hermes dashboard --host 0.0.0.0 --insecure --no-open"
```
3. Recheck with Python socket connect before `curl`.

### B) Port-wide firewall + local access
If iptables has:
    -A INPUT -p tcp --dport 9119 -j DROP
    -A INPUT -i tailscale0 -p tcp --dport 9119 -j ACCEPT
then local TCP probes fail.

Fix options:
1. Add local exceptions. Example: allow 127.0.0.1 before the DROP:
   `iptables -I INPUT -i lo -p tcp --dport <port> -j ACCEPT`
2. Use a local loopback-only listener (`--host 127.0.0.1`) instead of 0.0.0.0.
3. Prefer nginx path exposure when that’s already in use:
   - proxy_pass to backend
   - SELinux + perms already handled by existing exposure paths

### C) `--insecure`/diagnostics editors that block deletion
Some tools open a web editor for UI settings and refuse path changes. Workaround:
- Close the editor explicitly from the launch menu if present.
- Edit config/YAML directly when the UI blocks editing.

### D) SELinux / shared paths
- Backend proxies may need `setsebool -P httpd_can_network_connect on`.
- Project files under `/usr/share/nginx/html/projects/<name>` should be `nginx:nginx`.

## Decision Tree
```
Port ‘listening’ yet curl times out?
  -> SYN-RECV pileup? accept-loop bug; restart without shell background.
     Is route via tailscale0 only? firewall port DROP; add loopback/local rules or nginx path.
     Otherwise read app logs for hang after handshake.
‘Luckily worked once then stopped’ without source change?
  -> Re-run socket-level test; if same -> OS layer (firewall/iptables/SELinux/loopback).
```

## References
- `references/iptables-tailscale-port-block.md` — reproduction recipe and filter diff for the DROP+tailscale ACCEPT pattern.
