# Data-backed checkout preview verification

Use when an isolated SPA preview exercises API DTO changes, database writes, uploaded media, or provider checkout.

## Runtime isolation

- Run a separate API against a separate database copy and inject its API base into preview HTML.
- Override only isolation settings (`ADDR`/host/port and DB path); retain the runtime variables required by the flow, especially payment test configuration.
- Check environment precedence: `ADDR` may override `HOST`/`PORT`. Verify the actual listening socket is the preview address, not production.
- Verify the injected API base both at origin and publicly with a cache-buster.

## Checkout proof

1. Validate provider test credentials with a safe read-only request.
2. Exercise checkout through the public preview while authenticated.
3. Inspect the preview API log for the actual `POST /checkout` status and response cause.
4. Test direct booking/claim and package payment separately.
5. Assert the exact final pathname, such as `/wallet`; health, quote, build, and HTTP 200 checks do not prove checkout.

## DTO and media proof

For new card data such as coach avatars, inspect the authenticated preview JSON for the new field, then fetch the referenced media and verify its MIME type. A frontend fallback can hide a broken API contract, so rendered initials alone are not proof that profile-picture fetching works.

Keep requested controls visible when backing collections are empty and show concise empty states rather than hiding the whole section.
