# Komuna voucher + subscription session access

Use when fixing Komuna session booking, session banners, wallet/package entitlements, or `/programs/:id/vouchers/summary`.

## Durable model

Komuna session access can come from either:

1. An active voucher for the session product.
2. An active product-scoped subscription for the session product.
3. An active program-wide subscription where `subscriptions.product_id IS NULL` and `subscriptions.program_id` matches the session product's program.

Do not let a voucher-only UI/API gate block subscription users.

## Backend pattern

For Go local API booking (`api/v1/booking_handlers.go`):

- Try FIFO active voucher first, ordered by soonest `expired_at`.
- If no voucher, query active subscriptions by joining the session product to its program:
  - `JOIN products p ON p.id = ?`
  - require `s.program_id = p.program_id`
  - require `(s.product_id = ? OR s.product_id IS NULL)`
  - prefer product-specific subscriptions before program-wide: `ORDER BY CASE WHEN s.product_id=? THEN 0 ELSE 1 END, s.expires_at`
- Insert voucher claim with `subscription_id` and `claimant_id = subscription.program_member_id`; do not mark any voucher claimed.

## Summary endpoint pattern

For `/programs/:id/vouchers/summary`, keep old voucher fields for compatibility and add subscription fields:

- `programTotalActive`: active, unexpired voucher count only.
- `subscriptionTotalActive`: active, unexpired subscriptions in the program.
- `programSubscriptionActive`: true when any active subscription has `product_id IS NULL`.
- `perProduct[].subscriptionActive`: true when an active product-scoped subscription covers that product.

Filter active vouchers by both `status='active'` and `expired_at > now()`; old rows are lazily expired.

## Frontend pattern

`VoucherSummaryDTO` should include optional subscription fields so old responses remain safe:

```ts
interface VoucherSummaryProductDTO {
  productId: string
  productName: string
  activeCount: number
  subscriptionActive?: boolean
}
interface VoucherSummaryDTO {
  programTotalActive: number
  subscriptionTotalActive?: number
  programSubscriptionActive?: boolean
  perProduct: VoucherSummaryProductDTO[]
}
```

Booking modal access gate:

```ts
const productSummary = voucherSummary?.perProduct.find((p) => p.productId === session.productId)
const hasSubscription = Boolean(productSummary?.subscriptionActive || voucherSummary?.programSubscriptionActive)
const hasAccess = (productSummary?.activeCount ?? 0) > 0 || hasSubscription
```

Banner UI pitfall: if the user has no vouchers but has subscription access, show a positive access banner, not a “no vouchers / buy one” banner. For product-scoped subscriptions, prefer copy like:

> You have an active subscription for {productName}

Hide the purchase CTA when `hasAccess` is true.

## Tests to add

- Summary returns `subscriptionTotalActive`, `programSubscriptionActive`, and per-product `subscriptionActive` for product + program-wide subscriptions.
- Claim creation succeeds using a program-wide subscription when there is no voucher.
- Sessions banner renders subscription-only access copy and hides the Buy button.

## Verification checklist

- Run focused tests first and confirm they fail before implementation.
- Run `go test ./...` under `api/v1`.
- Build frontend with `unset VITE_NEON_AUTH_URL; npm run build`.
- Deploy frontend static assets and grep deployed JS for the new banner/modal copy.
- Restart and verify the Go API service if backend code changed.
