# Deferred subscription renewal cancellation

Use when a wallet or entitlement UI offers “Cancel renewal” but access must continue through the paid expiration time.

## Contract

- The first click opens an accessible confirmation dialog; it must not call the API.
- Copy states the exact access-through date/time and that cancellation takes effect immediately after expiration.
- Confirmation records cancellation intent (for example `cancel_at = expires_at`) while leaving entitlement status `active`.
- Eligibility and booking queries continue to use active status plus `expires_at > now`; scheduled cancellation must not revoke current access.
- The wallet returns `cancel_at`, disables repeat cancellation, and labels the entitlement “Renewal canceled.”
- Audit the intent as renewal cancellation, not immediate subscription cancellation.

## Regression coverage

1. UI: click “Cancel renewal”; assert no POST before confirmation and dialog copy includes the expiry date.
2. UI: confirm; assert the endpoint is called and active-through feedback appears.
3. API: assert status remains `active` and `cancel_at == expires_at`.
4. Build both backend and frontend.

## Deployment verification

For Go + Vite deployments, verify source → backend binary → running service health and source → Vite `dist` → actual nginx document root → origin bundle marker. Do not assume a similarly named web directory is the live root; inspect nginx configuration. CDN HTML can remain stale, so verify the origin first and use a cache-busted public HTML request afterward.

When the repository has unrelated failing tests, report focused regression/build results as targeted or ad-hoc evidence, not “the suite is green.” If the harness requests fresh evidence, create an OS-safe temporary script with `mktemp /tmp/hermes-verify-...`, run focused checks, and remove it afterward.
