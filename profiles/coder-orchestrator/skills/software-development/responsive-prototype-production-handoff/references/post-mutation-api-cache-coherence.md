# Post-mutation API cache coherence

Use when a public browser flow successfully submits a mutation but the UI does not show the new state after its follow-up read.

## Diagnostic sequence

1. Confirm the mutation response independently (status and returned ID).
2. Read the collection directly with the same authenticated session and verify the new record exists.
3. Instrument browser responses for the mutation and subsequent collection request.
4. If persistence is correct but the browser renders an older collection, inspect response caching before changing React state logic.
5. For authenticated application JSON that must reflect immediate mutations, emit `Cache-Control: no-store` at the shared API response boundary.
6. Add a backend regression asserting the cache header on a representative API response.
7. Rebuild from the clean committed SHA, redeploy that exact artifact, and rerun the same public browser mutation → refresh assertion.

## Why this matters

A component can correctly call its reload function while an intermediary or browser reuses a cacheable GET response. Fixing the shared API boundary is shorter and safer than adding cache-busting query strings to every frontend read.

## Browser-E2E interpretation

- Duplicate visible labels are a selector-scoping problem when multiple valid cards share the same action. Scope to the intended card or use `.first()` only when order is part of the contract; do not call this a product failure.
- An initial `401` from an intentional `/api/me` session probe is expected on a public login page. Record it separately from unexpected console/network failures.
- A strict CSP blocking an optional CDN analytics beacon can be expected and security-positive. Do not weaken `script-src` merely to silence analytics unless analytics is an explicit requirement.
- Require the final assertion to observe the newly created domain value in rendered UI, not merely a successful POST.
