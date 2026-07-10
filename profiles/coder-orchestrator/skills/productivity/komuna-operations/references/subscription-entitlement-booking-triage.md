# Subscription entitlement booking triage

Use when a Komuna member can see an active subscription in Wallet but sessions or booking modals say they have no vouchers/benefits.

## Symptom pattern

- `/wallet` shows active `subscriptions` for the user.
- All Sessions / Upcoming Sessions banner says “no vouchers left” or `0 active voucher`.
- Booking modal shows the no-voucher branch and routes to packages instead of allowing booking.
- A paid subscriber may be blocked or prompted to buy again.

## Root-cause checklist

Inspect both live Go API and React surfaces; the newer TS service may already contain the correct pattern but not be the deployed path.

### Live Go API

1. `api/v1/program_handlers.go` — `programVouchers` summary endpoint.
   - Bad pattern: summary built only from `vouchers`:
     ```sql
     SELECT v.product_id, p.name, COUNT(*)
     FROM vouchers v ...
     WHERE pm.program_id=? AND pm.user_id=? AND v.status='active'
     GROUP BY v.product_id, p.name
     ```
   - Fix shape: keep `/programs/:id/vouchers/summary` compatible, but count active subscriptions too.
   - Preserve existing fields: `programTotalActive`, `perProduct[].activeCount`.
   - Add optional explicit fields: `activeVoucherCount`, `activeSubscriptionCount`, `perProduct[].voucherCount`, `perProduct[].subscriptionCount`.

2. `api/v1/booking_handlers.go` — `createClaim` subscription fallback.
   - Bad pattern: subscription lookup only matches `s.product_id=?`.
   - Fix product-specific + program-wide access:
     ```sql
     WHERE pm.user_id=?
       AND s.program_id=?
       AND (s.product_id=? OR s.product_id IS NULL)
       AND s.status='active'
       AND s.expires_at > ?
     ORDER BY s.expires_at
     LIMIT 1
     ```
   - Claim should insert `voucher_claims.subscription_id` and leave `voucher_id` null.

3. Keep voucher FIFO unchanged for voucher-backed claims.

### React frontend

1. `apps/web/src/pages/all-sessions/BookingModal.tsx`
   - Bad pattern: `hasVoucher = productVoucherCount > 0` from `voucherSummary.perProduct[].activeCount`.
   - Fix: rename local logic to `hasBookingBenefit`; treat `activeCount` as entitlement count, not voucher count.
   - Use `voucherCount` / `subscriptionCount` only for copy.
   - Show Buy Package only when `activeCount === 0`.

2. `apps/web/src/pages/all-sessions/VoucherBanner.tsx`
   - Replace voucher-only zero-state copy with entitlement-aware copy:
     - no benefits: “no active booking benefits”
     - subscription-only: “active subscription”
     - voucher-only: existing voucher language OK
     - mixed: “active booking benefits”

3. `apps/web/src/lib/api-types.ts` and `apps/web/src/types/session-card.ts`
   - Add optional entitlement-aware count fields without breaking existing consumers.

4. Audit pages that pass `voucherSummary` into booking modal:
   - `apps/web/src/pages/AllSessionsPage.tsx`
   - `apps/web/src/pages/ProductDetailPage.tsx`
   - `apps/web/src/pages/ProgramDetailPage.tsx`

## Regression tests

- Summary counts active vouchers only.
- Summary counts active product-specific subscriptions only.
- Summary counts active program-wide subscriptions (`product_id IS NULL`) for eligible session products in the program.
- Expired/cancelled/refunded subscriptions are excluded.
- Booking with product-specific subscription creates a claim with `subscription_id`.
- Booking with program-wide subscription creates a claim with `subscription_id`.
- Booking modal renders confirm action when `activeCount > 0` from subscription-only summary.
- Banner does not say “no vouchers left” when subscription count is positive.

## Verification

```bash
cd /home/ubuntu/projects/komuna/api/v1 && go test ./...
cd /home/ubuntu/projects/komuna/apps/web && npm run test -- --run src/__tests__/all-sessions/AllSessionsPage.test.tsx
cd /home/ubuntu/projects/komuna/apps/web && npm run build
```

Manual probe after deploy:

1. Sign in as affected member.
2. `/wallet` shows active subscription.
3. `/programs/<program>/vouchers/summary` returns a positive entitlement count.
4. Session banner is not a voucher-only zero state.
5. Booking modal offers confirm booking.
6. `POST /claims` succeeds and creates `voucher_claims.subscription_id`.
