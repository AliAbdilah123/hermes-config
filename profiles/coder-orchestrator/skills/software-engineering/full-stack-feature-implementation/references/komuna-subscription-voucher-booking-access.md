# Komuna voucher + subscription booking access

Use when changing Komuna session booking, wallet/summary, or entitlement access in the local Go + SQLite + Vite deployment.

## Durable pattern

- The live local stack is the Go API under `api/v1` plus React/Vite under `apps/web`; do not only patch the old Hono/Drizzle API when public behavior is served by Go.
- `/programs/:id/vouchers/summary` feeds the session banner and booking modal. It must represent both voucher and subscription entitlement access, not voucher counts only.
- Preserve existing voucher fields for compatibility, then add subscription fields rather than replacing the shape:
  - `programTotalActive`: active, unexpired vouchers only.
  - `subscriptionTotalActive`: active, unexpired subscriptions in the program.
  - `programSubscriptionActive`: true when an active program-wide subscription has `product_id IS NULL`.
  - `perProduct[].subscriptionActive`: true for active product-specific subscriptions.
- Booking should grant access when any one of these exists:
  1. active unexpired voucher for the session product,
  2. active unexpired subscription for the session product,
  3. active unexpired program-wide subscription for the session program (`product_id IS NULL`).
- Prefer product-specific subscriptions over program-wide subscriptions when both match.

## TDD coverage to add first

- Summary endpoint test with both a product subscription and a program-wide subscription; assert `subscriptionTotalActive`, `programSubscriptionActive`, and product `subscriptionActive`.
- Booking test with only a program-wide subscription and no voucher; assert claim creation uses `subscription_id`.

## Implementation notes

- In Go SQL, find program-wide subscription eligibility by joining the session product to its program:
  `JOIN products p ON p.id=?` then `s.program_id=p.program_id AND (s.product_id=? OR s.product_id IS NULL)`.
- Keep the frontend confirm gate named around access, not vouchers: e.g. `hasAccess = voucherCount > 0 || hasSubscription`.
- Build frontend with `unset VITE_NEON_AUTH_URL; npm run build` before deploying Komuna Vite assets.
