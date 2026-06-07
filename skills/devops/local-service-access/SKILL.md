---
name: local-service-access
title: Local Service Access
description: Make a locally-bound service reachable from other devices securely. Covers Tailscale mesh access, SSH tunnels, reverse proxies, and applies to cases like exposing the Hermes dashboard.
---

# Local Service Access

Prefer mesh VPN or authenticated tunnel over raw public exposure.

## 1) Bind and expose over Tailscale

- Update the service to bind to `0.0.0.0`.
- Access it from a peer via the host's Tailscale IP.
- Optional firewall restriction to Tailscale CIDR `100.64.0.0/10`.

## 2) Connect via SSH tunnel

Keep the service bound to `127.0.0.1`. Connect with:
`ssh -L <local_port>:localhost:<service_port> user@host`

## 3) Reverse proxy

Keep the service on localhost. Expose through an existing reverse proxy
(e.g. nginx, caddy) if you already have HTTPS and auth in front.

## Applied example: Hermes dashboard on 9119

- Active compose file: `~/.hermes/hermes-agent/docker-compose.yml`
- Change dashboard command host to `0.0.0.0` for Tailscale access.
- Do not update only `./hermes-config/...` or `/tmp/hermes-config/...` copies, as the host may not use those.

## Checklist

- [ ] Service is bound to the intended interface (`0.0.0.0` or tunnel).
- [ ] Firewall matches intended exposure.
- [ ] A peer on the allowed path can reach the service.
- [ ] Public internet exposure is not enabled unintentionally.
