# Cloudflare nested-hostname TLS diagnosis

Use when moving an application to a proxied hostname with two or more labels below the zone, such as `dev.app.example.com`.

## Failure signature

- DNS resolves to Cloudflare anycast addresses.
- Public HTTP reaches Cloudflare and may redirect to HTTPS.
- Public HTTPS fails during TLS negotiation with `sslv3 alert handshake failure` and presents no peer certificate.
- Direct origin HTTPS succeeds and presents the expected Let's Encrypt certificate.

This separates an edge-certificate problem from nginx, application, origin-certificate, and firewall problems.

## Deterministic checks

```bash
# Origin routing and certificate, bypassing Cloudflare
curl -fsS --resolve <host>:443:127.0.0.1 https://<host>/
openssl s_client -connect 127.0.0.1:443 -servername <host> </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates

# Public edge
curl -fsSI https://<host>/
openssl s_client -connect <cloudflare-ip>:443 -servername <host> </dev/null
```

If the first pair succeeds and the second pair returns no certificate, fix Cloudflare edge coverage for the exact hostname. Universal SSL generally covers `example.com` and `*.example.com`, not a deeper hostname such as `dev.app.example.com`. Use Advanced Certificate Manager, a custom edge certificate, or a hostname covered by the existing certificate.

## Completion gate

Do not report the public-access move as complete based only on `curl --resolve`, certbot success, DNS resolution, or public HTTP. The done check is a normal public HTTPS request that returns the expected application HTML, followed by at least one asset request and one deep-route request.