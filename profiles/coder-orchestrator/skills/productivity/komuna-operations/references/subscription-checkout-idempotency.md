# Subscription checkout idempotency

Use this playbook when a Komuna package grants subscription benefits and checkout must reject duplicate active entitlements.

## Rule

Idempotency is entitlement-scoped, not merely package-ID-scoped. Reject checkout when the same user already has an `active` subscription whose `expires_at` is in the future and whose entitlement overlaps a subscription entry in the requested package. Allow checkout when the subscription is expired, its status is not active, or it covers a different product.

## Minimal Go + SQLite guard

Place the guard in the authenticated checkout handler before creating `program_members`, `purchases`, or `purchase_items` rows. Join:

- `subscriptions` to `program_members` to scope by authenticated `user_id`
- requested package's `package_entries` filtered to `benefit_type='subscription'`
- matching product entitlement (`s.product_id = pe.product_id`), retaining `s.product_id IS NULL` only if null means program-wide entitlement in the current schema
- program scope, active status, and `expires_at > now()`

Return HTTP 409 with a stable domain error such as `already_subscribed_package`. Confirm that rejection creates zero purchase records.

## Regression matrix

1. Matching active, future-dated entitlement: 409; no purchase row.
2. Matching entitlement with `status='expired'`: checkout proceeds.
3. Matching entitlement still marked active but past `expires_at`: checkout proceeds.
4. Active future-dated entitlement for another product: checkout proceeds.
5. Voucher-only package: unaffected.

Run focused tests first, then `go test ./...` from `api/v1`.

## Paid fulfillment and recovery paths

Audit every path that converts a paid purchase into benefits, not only the normal webhook/confirmation path. Komuna may also recover pending payments in a background job. Every recovery helper must branch on `package_entries.benefit_type`: create exactly one `subscriptions` row for a subscription entry regardless of its legacy `quantity`, and create `quantity` voucher rows only for voucher entries. Reuse the same validity calculation as normal fulfillment.

Add a focused regression that seeds a subscription entry with an intentionally large quantity (for example 999), invokes the recovery helper directly, and asserts zero vouchers plus one subscription. This catches the database-bloating failure mode that ordinary quantity-1 fixtures conceal.

## Correcting misclassified live package data

When a package intended as a subscription was stored as a high-quantity voucher entry:

1. Back up the live SQLite database with `.backup` before mutation.
2. Identify the affected user by stable identity, all memberships, purchases, package entries, vouchers, claims, and existing subscriptions. Duplicate user rows can exist, so scope through `users -> program_members` rather than assuming one user ID.
3. Confirm whether purchase vouchers have claims. Delete dependent `custom_field_answers` and `voucher_claims` before deleting only the affected user's purchase-generated vouchers; preserve giveaway and compensation vouchers unless explicitly requested.
4. Restore the package entry to `benefit_type='subscription'`, normalize quantity to 1, and set the intended validity semantics.
5. Create at most one subscription entitlement for the appropriate paid purchase using `NOT EXISTS` on purchase and product. Do not convert every historical purchase into a simultaneous active subscription unless that policy is explicitly requested.
6. Commit, run `PRAGMA integrity_check`, and verify package semantics, zero targeted purchase vouchers, and exactly the intended subscription rows.

## Verification and deployment

A source fix is incomplete if the running recovery worker still uses an old binary. Build the service artifact, deploy it to the exact systemd `ExecStart` path, restart, and probe the API health route. Keep focused verification evidence separate from full-suite status: if unrelated tests fail, report the focused regression as ad-hoc passing rather than claiming the suite is green. When required, create the verifier with `mktemp /tmp/hermes-verify-...`, run it, and remove it with a trap.

## Pitfalls

- Fixing only primary paid fulfillment leaves background payment recovery free to recreate voucher floods.
- Treating a large voucher quantity as an “unlimited subscription” is not equivalent: it bloats storage and bypasses subscription entitlement semantics.
- Checking only package ID misses different packages that grant the same entitlement.
- Checking only status incorrectly blocks stale active rows past their expiry.
- Do not compare mixed SQLite timestamp encodings as plain text. Rows may contain both RFC3339 values (`2099-01-01T00:00:00Z`) and SQLite `datetime()` values (`2099-01-01 00:00:00`), whose lexical ordering can bypass an otherwise-correct future-expiry guard. Normalize both sides in SQL, for example `julianday(s.expires_at) > julianday(?)`, and include a regression fixture created with `datetime('now', '+1 hour')`.
- Creating a pending purchase before the guard leaves duplicate/abandoned purchase state.
- Verify rejection leaves purchase count unchanged; if the member already existed, assert its count remains unchanged rather than incorrectly expecting zero members.
- Avoid broad uniqueness constraints unless expiry/status semantics can be represented safely; a checkout transaction guard is the minimum compatible implementation, while concurrency-hardening may later require a database-backed reservation or constraint strategy.
