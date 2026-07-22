# Booking cancellation compensation vouchers

Use this playbook when a Komuna member cancellation must immediately restore value according to a session product's cancellation tiers.

## Durable design

- Keep policy evaluation on the Go API. Both preview and mutation must call the same evaluator so UI copy cannot diverge from the voucher actually issued.
- Add an ownership-protected preview endpoint that reports the applied time band, refund type, voucher validity, expected expiry, product name, and session start.
- Treat cancellation, occupancy decrement, optional compensation-voucher insertion, and audit writes as one SQLite transaction.
- Preserve the consumed voucher as history. Issue a new active voucher with `source='compensation'` and `origin_claim_id=<cancelled claim>` when the tier allows a refund.
- Subscription-backed bookings release the booking but do not create a voucher because no voucher was consumed.
- Inside a no-refund period, allow cancellation but state clearly that no voucher will be issued.

## Idempotency and concurrency

A conditional `cancelled_at IS NULL` update alone is insufficient. Concurrent requests can contend or future database behavior can permit duplicate compensation rows.

- Serialize the mutation at the application boundary when using a shared SQLite connection.
- Add a partial unique index on `vouchers(origin_claim_id) WHERE origin_claim_id IS NOT NULL`.
- On a repeated cancellation, return the already-completed cancellation/refund result rather than creating another voucher or surfacing a generic 500.
- Test both repeated and concurrent requests, asserting successful/idempotent responses and exactly one compensation voucher.

## Frontend contract

- Open an accessible modal before mutation and fetch the server preview after the user clicks Cancel.
- Show loading/error states, the qualifying period, refund outcome, voucher type, validity, and expiry.
- Support Escape, backdrop close, focus restoration, and duplicate-submit prevention.
- After success, navigate to Wallet with one-time route state. Wallet consumes that state and shows the appropriate toast; use the voucher-refund toast only when a voucher was actually issued.

## Verification matrix

Backend tests: owner-only access; early/middle/no-refund tiers; malformed policy; subscription booking; past/attended claim; occupancy floor; retry and concurrent idempotency; exactly one voucher and correct expiry.

Frontend tests: modal semantics and focus; preview copy; refund/no-refund/subscription states; failed submission remains open; one POST; Wallet redirect; toast consumed once.

Before delivery, run focused and relevant full Go tests, focused frontend tests, production build, independent review, then stage only named feature files in a dirty worktree. Commit and push after verification; deploy only when separately authorized.