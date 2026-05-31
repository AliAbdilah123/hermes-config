---
name: network-service-binding
title: Network Service Binding & Tailscale Exposure
description: Diagnose and fix services that work locally (127.0.0.1) but are unreachable over Tailscale or from other nodes. Covers bind-address verification, firewall/SELinux checks, and reconfiguration.
trigger:
  - "service is up locally but not reachable by IP"
  - "port answered on 127.0.0.1 but not on host/Tailscale IP"
  - "tailscale is online yet connection refused"
---

# Network Service Binding & Tailscale Exposure

## Quick Diagnosis

1. **Check where the service is listening:**
   `ss -tlnp | grep <PORT>`
   If it shows `127.0.0.1:<PORT>`, the service is localhost-only.

2. **Verify Tailscale state and IP:**
   `tailscale status --json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('Self',{}).get('TailscaleIPs',[])); print('Online:', d.get('Self',{}).get('Online'))"`

3. **Check firewall:**
   `systemctl is-active firewalld`
   If inactive, firewall rules are not the culprit.

4. **Check SELinux (only for HTTPD/nginx proxy cases):**
   `getsebool httpd_can_network_connect`
   If `off`, the web server cannot proxy to upstreams on other interfaces.

## Common Root Causes

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Listen addr is `127.0.0.1` | Service defaulted to loopback | Reconfigure to `0.0.0.0` or the Tailscale IP |
| HTTPD proxy upstream unreachable | SELinux boolean off | `setsebool -P httpd_can_network_connect on` |
| Connection refused on public IP | Port not open in zone/config | Open in firewall or nginx listeners |

## Fixing Localhost-Only Services

- Hermes TUI/gateway specifically: use `--host 0.0.0.0` or the config field to override bind.
- Generic Go server: ensure `Listen` uses `0.0.0.0` (or the Tailscale IP), not `127.0.0.1`.

## Reference

See `references/service-exposure-checklist.md` for environment-specific notes and diagnostic output patterns.
