# Wrong Healthy Upstream Diagnosis

Use when a public app returns a valid but unexpected response—often surfaced by the frontend as “Invalid server response”—while its intended local service appears healthy.

## Why this is deceptive

DNS/TLS/CDN/nginx can all work, and the configured upstream port can have a healthy listener, yet that listener belongs to another application. The wrong service may return JSON health successfully but plain-text 404 or an incompatible envelope for login.

## Evidence chain

1. Capture the exact browser request path, method, content type, status, and raw body. Do not substitute a guessed endpoint.
2. Inspect the frontend URL builder and effective nginx location to establish the expected public-to-local mapping.
3. Run `ss -ltnp` for the configured and suspected ports. A listening port is not proof that the intended process owns it.
4. Probe a service-specific endpoint on both ports. Compare semantic markers, not only status; for example, `{"ok":true}` versus `{"status":"ok"}` distinguishes two healthy services.
5. Use `nginx -T` to identify both the effective route and source config file.
6. If source and local tests already satisfy the contract, change only that location's `proxy_pass`; the same old port may legitimately serve another route.
7. Run `nginx -t`, reload, inspect the effective block again, and issue a cache-busted public health probe.
8. Finish with the exact authenticated public browser flow, console/network checks, and logout/session behavior. HTTP 200 and health are supporting evidence, not login E2E.

## Guardrails

- Preserve unrelated repository modifications.
- Do not restart either healthy app until ownership and route mapping prove it necessary.
- Do not manufacture an application commit for an nginx-only defect. Report the runtime configuration fix and existing main/upstream state honestly.
- A malformed-login probe is useful only on the exact frontend route and JSON shape. A guessed `/api/auth/login` when the app uses `/api/login` creates misleading evidence.
- Read back effective config after reload rather than trusting the edited file alone.
