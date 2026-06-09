---
name: service-exposure-debugging
description: "Service unreachable/broken exposure debugging: ports, firewalls, SELinux, nginx, Tailscale, localhost-only loopback aliases, proxy-ready paths, and restart loops. This is the consolidated umbrella for all service-exposure and fullstack-deployment knowledge; see the references/ directory for absorbed skill content."
version: 1.0.1
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [debugging, networking, linux, tailscale, selinux, iptables, nginx, port-forwarding, fullstack-deployment, nginx-config]
    related_skills: [network-service-binding, release-and-expose-web-app, standard-stack-scaffold, default-web-stack, fullstack-app]
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

## Response Style
- User prefers concise, direct answers. Give result or next concrete step; avoid verbose explanation unless asked.

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

### E) Static frontend projects under /home/<user> and path-based exposure
Use this when nginx is inbound-blocked from serving `/home/...` directly or when the nginx runtime user cannot traverse home dirs.

1. Use a stable root under `/var/www/html/projects/<name>`.
2. Copy each project's known-good `frontend/` directory there with `cp -a`.
3. Route all projects under shared `/projects/` prefix instead of separate ports per project.
4. Do not leave stale directories like `omnichannel-chat-hub` if canonical name is `projects-omnichannel-chat-hub`; duplicate dirs cause 404 surprise.

Example layout:
```
/var/www/html/projects/demo/index.html
/var/www/html/projects/insta-scheduler/index.html
/var/www/html/projects/omnichannel-hub/index.html
/var/www/html/projects/projects-omnichannel-chat-hub/index.html
/var/www/html/projects/system/index.html
```

## Decision Tree
```
Port ‘listening’ yet curl times out?
  -> SYN-RECV pileup? accept-loop bug; restart without shell background.
     Is route via tailscale0 only? firewall port DROP; add loopback/local rules or nginx path.
     Otherwise read app logs for hang after handshake.
‘Luckily worked once then stopped’ without source change?
  -> Re-run socket-level test; if same -> OS layer (firewall/iptables/SELinux/loopback).
```

## Absorbed content from network-service-binding

- `references/network-service-binding-iptables-port-names-pitfall.md` — iptables port-name translation pitfall (numeric vs. service-name resolution), verbatim delete workflow.
- `references/network-service-binding-service-exposure-checklist.md` — sample diagnostic output, environment facts (Oracle Linux 9, nginx 1.20.1, SELinux enforcing), and local routing check for port 9119 and Tailscale IP.

## Absorbed content from release-and-expose-web-app

- `references/release-and-expose-nginx-root-return-fix.md` — patch pattern for returning a plain text body from `/` via `/etc/nginx/projects/default.conf`, reload checklist.
- `references/release-and-expose-oracle-linux-nginx-selinux.md` — Oracle Linux 9 SELinux + nginx checklist for home-dir serving, `httpd_can_network_connect`, preferred `/usr/share/nginx/html/<project>/` layout.

## Absorbed content from standard-stack-scaffold

- `references/standard-stack-port-sharing-lessons.md` — Duplicate `server_name _` fix, port 8080 occupied fallback to 9090, `nginx.conf` inclusion paths (`/etc/nginx/conf.d/*.conf`), relative API path guidance.
- `references/standard-stack-monitor-frontend-pattern.md` — Reusable production pattern for TS/React system monitors under `/projects/<project>/`, Go endpoints, nginx exposure, frontend fetch-base rule.

## Original references

- `references/iptables-tailscale-port-block.md` — reproduction recipe and filter diff for the DROP+tailscale ACCEPT pattern.
- `references/oci-public-ingress-verification.md` — OCI-side verification flow for externally unreachable but locally-reachable web services: metadata/VNIC facts, security-list ingress audit, and the required OCI CLI command form.
- `references/network-service-binding-iptables-port-names-pitfall.md` — iptables port-name translation pitfall (numeric vs. service-name resolution).
- `references/network-service-binding-service-exposure-checklist.md` — sample diagnostic output and environment facts.
- `references/release-and-expose-nginx-root-return-fix.md` — patch pattern for returning a plain text body from `/` via `/etc/nginx/projects/default.conf`, reload checklist and root-return pitfalls.
- `references/release-and-expose-oracle-linux-nginx-selinux.md` — Oracle Linux 9 nginx + SELinux fix checklist for home-dir serving and static asset placement.
- `references/standard-stack-port-sharing-lessons.md` — port 8080 occupied fallback, duplicate `server_name _` fix, relative API path guidance, `nginx.conf` inclusion paths.
- `references/standard-stack-monitor-frontend-pattern.md` — reusable TS/React + Go system monitor pattern, frontend fetch-base rule.
- `references/fullstack-app-output-sequence.md` — fullstack-app deliverable contract: required output is a working public link, backend frontend fallbacks, and tail-validation order.
