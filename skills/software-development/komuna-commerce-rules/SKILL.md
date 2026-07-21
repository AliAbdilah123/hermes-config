---
name: komuna-commerce-rules
description: >
  Komuna backend commerce rules and verification recipes. Use when implementing
  or changing checkout, purchases, vouchers, subscriptions, package entitlements,
  auto-booking, or related business constraints in `api/v1`.
---

# Komuna Commerce Rules

Class-level skill for backend purchase, entitlement, and subscription behavior in
`api/v1`. Frontend prototypes are out of scope; use `komuna-prototype-deployment`
for UI work.

## Inventory

| Rule | Where enforced | Frontend hint |
|------|----------------|---------------|
| Subscription idempotency | `commerce_handlers.go` `checkout()` | Hides packages user already subscribes to |
| Active subscription blocks same-coverage package purchase | `subscriptions` + `package_entries` join | Shows “already subscribed” state |
| Expired/cancelled subscriptions allow repurchase | `expires_at > now()` check | Re-enable package after expiry |
| Voucher purchase has no per-user duplicate guard | existing flow | Repeat purchase allowed |
| Auto-booking uses existing member state | `booking_handlers.go` | Outcome reported in `booking_status` |

## Subscription idempotency

Trigger: user tries to buy a package whose `package_entries.benefit_type='subscription'`.

Enforcement points:
- `commerce_handlers.go` `checkout()` before transaction begins:
  - if package has subscription entries
  - and user has any `subscriptions.status='active' AND expires_at > now()`
  - that covers the same product (`s.product_id=pe.product_id OR s.product_id IS NULL`)
  - reject with `409 {"error":"already_subscribed_package"}`
- Do not create purchase, program_member, or checkout session.

## Repurchase after expiry

Expired (`status='expired'`) or past-expiry subscriptions do not block checkout.
Use `expires_at > now()` only for the guard.

## Product-coverage matching

A program-level subscription may have `product_id IS NULL` and still covers every
product in the program. The check must allow `product_id IS NULL` matches.

## Voucher packages

Voucher-only packages remain freely purchasable; do not add duplicate-blocking
logic there.

## Cancellation

`wallet/subscriptions/{id}/cancel` sets `status='cancelled'`. Cancelled
subscriptions do not block repurchase because the guard only scans
`status='active'`.

## Verification order

1. `go build ./...`
2. Targeted tests in `package_auto_booking_test.go` for checkout/subscription:
   - `TestCheckoutRejectsUserWithActiveSubscriptionForSubscriptionPackage`
   - `TestCheckoutAllowsSubscriptionPackageAfterExpiry`
3. Run the full suite: `go test ./...`

## Pitfalls

- Do not put the guard inside `finishPurchaseCore()`; payment already happened
  there. Block at `checkout()` before invoice creation.
- Package creation does not enforce subscription uniqueness; the guard is at
  purchase time only.
- Tests asserting JSON body equality should account for `json.Encoder` newline
  variance; prefer structured decode or byte comparison after trimming.
