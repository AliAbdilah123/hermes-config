# Exact provider callback routing and verification

Use this for third-party callback verification endpoints (Meta, payments, OAuth diagnostics) when only one public path should reach a backend.

## Minimal routing shape

Prefer an exact location instead of assigning a whole root API namespace:

```nginx
location = /api/integrations/<provider>/webhook {
    proxy_pass http://127.0.0.1:<port>/api/integrations/<provider>/webhook;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Install the same exact route in the hostname's HTTP and HTTPS server contexts when Cloudflare/origin mode may use either. Do not broaden to `location /api/` unless that hostname intentionally assigns the complete namespace to this service.

## TLS/SNI gate

A working HTTP `Host` probe does not prove HTTPS routing. Check effective 443 server blocks and origin SNI independently:

```bash
curl --resolve host.example:443:127.0.0.1 \
  'https://host.example/api/integrations/provider/webhook?...'

echo | openssl s_client -connect 127.0.0.1:443 -servername host.example 2>/dev/null \
  | openssl x509 -noout -subject -ext subjectAltName
```

If another application's certificate/content appears, create a dedicated `server_name` 443 vhost with a certificate covering the exact hostname. After `nginx -t`, a reload can leave old workers serving the old SNI mapping; if effective config is correct but SNI remains stale, perform a bounded nginx restart and retest.

For a callback-only hostname/vhost, keep the blast radius narrow:

```nginx
location = /api/integrations/<provider>/webhook { ... }
location / { return 404; }
```

## Verification chain

Use the real configured token without printing it. Require every layer to return the exact contract:

1. Direct upstream on loopback.
2. Origin HTTP with correct `Host`.
3. Origin HTTPS with correct SNI (`--resolve`).
4. Public HTTPS through CDN/DNS.
5. Wrong token is rejected with no token in body.
6. Unimplemented methods (for example POST during a GET-only feasibility phase) remain unavailable.

For Meta GET verification, success means exactly:

- status `200`;
- `Content-Type` beginning with `text/plain`;
- no redirect;
- body byte-for-byte equal to `hub.challenge`.

Do not infer success from status alone.

## Secret hygiene

Webhook verification tokens commonly appear in query strings and therefore in nginx access/error logs. Never print raw matching log lines in reports. Redact query strings before displaying diagnostics. Prefer configuring a callback-specific access log format that omits `$args` when operationally acceptable.

If an existing token must be preserved, use the authoritative restricted runtime secret source. Treat recovering it from historical request logs as emergency-only because it demonstrates that the secret has already been logged; after the feasibility gate, remove query arguments from callback logs and rotate only with explicit authorization.

## Deployment boundary

Application route presence, deployed binary freshness, Nginx proxying, TLS vhost selection, and CDN/public behavior are separate gates. Verify all five. A healthy service or correct source route does not prove the public callback reaches that route.
