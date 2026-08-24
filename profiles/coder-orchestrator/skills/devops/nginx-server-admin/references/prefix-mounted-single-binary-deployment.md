# Prefix-mounted single-binary SPA deployment

Use this pattern when one backend binary embeds the SPA and natively mounts both UI and API beneath the same public prefix.

## Preferred topology

- Build Vite with the exact base, e.g. `/projects/app/`.
- Configure React Router with basename `/projects/app`.
- Configure the API client to call `/projects/app/api/v1/...`.
- Configure the Go router/runtime with the exact base `/projects/app/`.
- Have nginx proxy the **entire prefix without stripping it**:

```nginx
location = /projects/app {
    return 308 https://example.com/projects/app/;
}
location ^~ /projects/app/ {
    proxy_pass http://127.0.0.1:18081;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Request-ID $request_id;
    proxy_set_header Connection "";
}
```

This avoids `sub_filter`, duplicate static deployments, API fallback ambiguity, and basename drift. Before reload, read back the config and confirm nginx variables such as `$request_id` remain literal.

## Verification ladder

1. Loopback prefixed health/readiness returns JSON.
2. Loopback unprefixed API returns 404, proving isolation.
3. Public HTML emits only prefix-qualified asset URLs.
4. Emitted JS/CSS return their real MIME types, never SPA HTML.
5. A real deep route renders in desktop and mobile browsers.
6. Auth runs through the public prefix; verify cookie `Secure`, `HttpOnly`, `SameSite=Lax`, and `Path=/projects/app/`.
7. Exercise two-user state through the public API and reload the exact feature route.
8. Verify an unrelated sibling route after nginx reload.
9. Confirm the backend listener is loopback-only.

## Cloudflare redirect cache diagnosis

A corrected exact-path redirect can remain stale at the edge. Do not keep changing nginx when:

- origin/SNI verification shows the corrected redirect; and
- a public cache-busted query shows the corrected redirect; but
- the bare cached URL still shows the old `Location`.

Verify origin with `curl --resolve` and public behavior with a cache-busting query. Treat the remaining mismatch as edge cache state, not an application defect.

## Authenticated E2E pitfalls

- Session bootstrap may rotate the CSRF token. After browser navigation/reload, do not reuse the token captured at initial OTP verification. Use the UI/API client's current token or fetch the current session again before a mutation such as logout.
- If using a local SMTP capture for preview verification, keep it loopback-only and root-controlled. The capture file must remain owned and writable by the service user; truncating it as root can silently change ownership and make OTP delivery fail with HTTP 500.
- Clear captured OTP mail after verification. A capture service is verification infrastructure, not a substitute for real SMTP for external pilot users.
