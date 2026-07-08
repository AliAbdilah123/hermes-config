# Subscription package entitlement model

Use this reference when updating Komuna subscription/package/voucher review artifacts or implementation plans.

## Domain language

- **Package**: the sellable bundle shown to buyers/admins.
- **Package entry**: one granted benefit inside the package.
- **Voucher**: concrete redeemable credit/access for a product/session.
- **Subscription entitlement**: renewable access source granted by a package entry while billing remains active.
- **Voucher claim / claimed voucher**: concrete booking/redemption usage. For subscription-backed bookings, `voucher_claims.subscription_id` is set and `voucher_id` is null.

## Planning rules

1. Do not model subscription as only a normal voucher; renewal/cancellation/payment state makes it an entitlement source.
2. Do model subscription as a package entry/grant so it can be sold in multiple packages.
3. A package may contain multiple entries and may mix subscription entries with voucher/product/bonus entries, unless the user explicitly chooses a simpler V1 restriction.
4. Subscription access can be scoped to one or more products.
5. Minimal V1 scope modeling: use multiple subscription package entries / multiple subscription rows, one per product, instead of adding a `subscription_products` join table immediately.
6. Program-wide subscription remains possible with nullable `subscriptions.product_id`, but treat it as a deliberate admin choice because it can over-grant access.
7. Do not pre-generate future claimed vouchers. Create the claim only when the member books/redeems.

## Acceptance checks to include

- Mixed package checkout issues vouchers for voucher entries and subscription rows for subscription entries.
- Duplicate subscription entries for the same product in one package are rejected.
- Product-scoped subscription for Product A cannot book Product B.
- Subscription-backed booking creates `voucher_claims.subscription_id` and no voucher consumption.
- Renewal extends/recreates entitlement access, not future booking claims.
