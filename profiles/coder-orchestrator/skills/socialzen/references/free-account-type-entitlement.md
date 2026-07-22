# Payment-exempt account entitlement

Use when a nullable user-level account classification must override subscription payment, warnings, and posting quotas without changing the ordinary free subscription tier.

## Contract

- Add nullable `users.accountType VARCHAR(30)` with no default.
- Only the exact value `FREE` grants the entitlement.
- `NULL`, `free`, `FREE `, empty, and all other values retain existing behavior.
- Keep this distinct from the subscription tier named `FREE`; do not infer exemption from `tier == "FREE"`.
- Keep `tier` unchanged in API responses. Expose a separate `accountType` and/or derived `paymentBypassed` flag.

## Backend boundaries

1. Update both SocialZen migration paths: production `internal/models/models.go` and legacy/test `db.go`, including fresh schema and compatibility `ALTER TABLE`.
2. Centralize the exact-match lookup in one entitlement helper to avoid divergent comparisons.
3. Bypass quota reservation at the shared reservation boundary in `internal/models/quota.go`; this covers create, duplicate, and deferred publishing without caller-specific branches.
4. Return unlimited quota semantics from subscription/dashboard DTOs for entitled users.
5. Short-circuit payment-bearing subscription actions and automatic continuation invoice generation. Stale payment-return URLs should return current exempt status without creating an invoice.

## Frontend boundaries

Suppress all subscription-pressure UI when `accountType === "FREE"`:

- global expiry/unpaid-invoice banner;
- renewal, cancellation, expiry, suspension, and downgrade warnings;
- subscribe/upgrade/downgrade/continue-payment actions;
- finite quota progress and “posts left” messaging;
- upgrade prompts on Dashboard, Plans, Payment Redirect, and Settings → Subscription.

Render a neutral payment-exempt/unlimited state instead. Frontend gates are UX only; backend payment and quota bypasses remain authoritative.

## TDD checks

- Both migrations create nullable `VARCHAR(30)` and preserve `NULL` for legacy users.
- Exact `FREE` can exceed ordinary limits and creates no quota reservation row.
- Near-matches remain limited.
- No provider request, payment URL, pending invoice, or pending plan mutation occurs for entitled users.
- UI tests prove banners, payment actions, finite quota copy, and upgrade prompts are absent.
- Ordinary free-tier and paid-account regressions remain green.

## Delivery

Run focused backend/frontend tests, full Go tests, frontend typecheck/build, deploy both changed surfaces, verify live API/assets, then commit and push while preserving unrelated untracked planning artifacts.

Verification must distinguish feature proof from unrelated suite health:

- Run entitlement-bearing Go packages and focused migration tests separately so the feature has explicit green evidence even if the repository-wide suite has pre-existing failures.
- Still run `go test ./...`; report every unrelated failing package/test by name rather than describing the full suite as passing.
- After deployment, prove the service is active, `/health` responds, `PRAGMA table_info(users)` contains nullable `accountType VARCHAR(30)`, the public SPA returns 200, the current JS asset is `application/javascript`, and deployed chunks contain the neutral entitlement copy.
- Stage implementation files explicitly. Do not sweep unrelated untracked plans/docs into the feature commit.
