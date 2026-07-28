# Xendit Payment Hardening and Expired Purchase Reconciliation

Use when auditing or implementing provider-backed package purchases in the active Komuna Go/SQLite API.

## Security invariants

- Authenticate callbacks with a constant-time comparison of `x-callback-token` against the configured callback token; fail closed.
- Never trust callback status or amount alone. Fetch the provider invoice and correlate provider invoice ID, `external_id`/purchase ID, exact amount, and currency.
- Permit only legal conditional transitions. Payment finalization should generally win with `UPDATE ... WHERE status='pending'`; stale terminal callbacks must not downgrade paid purchases.
- Fulfillment and the paid transition belong in one SQLite transaction. Check every query, scan, and insert error.
- Make fulfillment database-idempotent under duplicate/concurrent callbacks. Do not use a count-then-insert guard without durable uniqueness.
- Snapshot package-entry semantics at checkout so later package edits cannot change purchased quantity, product, validity, or benefit type.
- Require subscription-entry quantity to match defined semantics (currently exactly one).

## Checkout idempotency

- Generate one client idempotency key per package/session attempt and reuse it across retries.
- Enforce member-scoped idempotency with a database uniqueness constraint and return the existing purchase/invoice for repeated requests.
- Before retrying an ambiguous invoice creation, query Xendit by the deterministic purchase `external_id`. If a matching invoice exists, validate and adopt it instead of POSTing another invoice.
- This lookup-before-create rule also recovers when Xendit created the invoice but Komuna timed out, received malformed output, or failed to persist the provider response.
- Keep invoice creation state explicit (`creating`, `created`, `failed`) rather than leaving unusable generic pending rows.
- Use a bounded shared HTTP client. A network timeout is unknown/transient, not proof of payment failure.

## Expired purchase semantics

Keep these states distinct:

- `pending`: provider still says pending/payable.
- `expired`: provider explicitly says expired, or a trustworthy stored provider expiry passed when no usable provider invoice identity exists.
- `failed`: provider explicitly failed/cancelled according to policy.
- `paid`: verified and fulfilled.
- `refunded`: provider-confirmed terminal state; do not claim benefit revocation unless a real refund/revocation policy exists.

Provider truth wins. If Xendit returns `PENDING`, do not locally expire the purchase merely because its stored deadline appears elapsed. Transient lookup/network errors remain pending and retry later.

## Recovery scheduler

- Start reconciliation from the active application, run once at startup, then periodically (five minutes is a practical default).
- Select only recoverable pending attempts.
- Route webhook, success-page confirmation, and scheduler recovery through the same canonical verifier/finalizer.
- Paid fulfillment remains transactional and idempotent.
- Explicit expired responses transition to `expired` without issuing benefits.
- Do not mark unknown provider responses failed after an arbitrary retry count.

## SQLite migration pitfall

Adding `expired` to a status protected by a SQLite `CHECK` requires rebuilding the table, copying every payment-hardening column, restoring indexes/unique constraints, and testing migration from the actual legacy schema. An `ALTER TABLE` that only adds columns does not update the old status constraint.

## UX/API contract

- Payment return begins with **Confirming payment**, never success.
- Show success and redirect only after verified `paid`; handle pending, expired/failed, missing purchase ID, and transient error distinctly.
- Preserve `expired` in DTOs, filters, pagination/count summaries, admin Purchases, member Purchases, and profile Purchases.
- Label it **Expired** (Indonesian: **Kadaluarsa**) and offer a new-checkout action where appropriate.
- Exclude expired attempts from completed-purchase and spending totals; include them in admin problem/attention counts.

## Minimum regression matrix

1. Missing/wrong callback token is rejected.
2. Invoice identity, amount, currency, or external ID mismatch fails closed.
3. Concurrent duplicate callbacks issue exactly one expected benefit set.
4. Mid-fulfillment failure rolls back status and all benefits.
5. Repeated checkout requests create one purchase/invoice.
6. Ambiguous provider creation and local persistence failure recover with one provider POST.
7. Lost webhook is reconciled to paid exactly once.
8. Provider pending stays pending; transient error stays pending; provider expired becomes expired.
9. Legacy schema migrates and accepts expired while preserving indexes and columns.
10. Admin, member, and profile purchase views render/filter Expired.

## Reporting style

For stakeholder explanations, lead with a short verdict and a simple problem → solution table. Put implementation details and evidence afterward; avoid long threat-model prose unless explicitly requested.
