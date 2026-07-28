# Payment webhook and entitlement fulfillment hardening

Use when provider checkout works but callback processing or package delivery needs production hardening.

## Threat-to-fix map

| Risk | Minimum durable fix |
|---|---|
| Forged paid callback | Constant-time callback-token validation, then server-to-server verification of invoice ID, external purchase ID, amount, currency, and terminal status. Never trust callback status alone. |
| Paid purchase with missing/partial benefits | Issue all vouchers/subscriptions and transition the purchase to paid in one DB transaction. Check every query, scan, and insert; rollback on failure. |
| Duplicate benefits from retries/concurrency | Replace count-then-insert with DB-enforced idempotency: unique provider event IDs and deterministic per-entry entitlement units. Use a conditional pending-to-processing/paid update so one worker wins. |
| Late callbacks rewrite history | Enforce legal transitions with conditional SQL: pending to paid/failed/expired; paid to refunded only. Record stale callbacks without mutating benefits. |
| Missed webhook | Reconcile pending invoices by stored provider invoice ID and call the same canonical transactional finalizer. Unknown/network errors remain pending; only explicit terminal status fails. |
| Duplicate checkout invoices | Persist a client idempotency key under a unique user/key constraint and return the existing attempt. Disabling the Pay button is UX only. |
| Archived/empty package purchase | Require an active package with at least one valid active-product entry before creating provider state. Snapshot purchased entry semantics. |
| Misleading success UX | Start with “Confirming payment…”. Show/redirect success only after verified paid; handle pending, failed, and missing purchase ID separately. No independent countdown race. |
| Provider request hangs | Use one bounded HTTP client with connection, TLS, response-header, and total timeouts. |

## Fulfillment model

For quantity benefits, identify each unit deterministically, e.g. `(purchase_id, package_entry_id, unit_number)`, and enforce uniqueness. For subscriptions, use one deterministic fulfillment record per purchased entry. A mixed package commits every expected entitlement or none.

Simple products need an explicit product decision: redeemable items should be labeled and tracked as vouchers; shipped goods require an order, inventory reservation, shipping/pickup details, and fulfillment state. A voucher alone is not physical delivery.

## Required TDD cases

1. Missing/wrong callback token.
2. Mismatched invoice ID, amount, currency, or external ID.
3. Concurrent paid callbacks issue exactly the expected benefits.
4. Forced mid-fulfillment failure leaves the purchase unfinalized with zero benefits.
5. Late failed callback leaves paid purchase unchanged.
6. Missed webhook recovers exactly once.
7. Duplicate checkout requests return one purchase/invoice.
8. Archived, empty, and invalid packages are rejected before invoice creation.
9. Success UI stays neutral for delayed/pending/failed/missing-ID confirmation.

Keep credential validity, provider mode, checkout activity, callback safety, and fulfillment correctness as separate conclusions. A passing happy path does not prove production readiness.

## Stakeholder reporting

Lead with the verdict. Use a concise problem/solution table and list release blockers first. Put detailed implementation mechanics and evidence in an appendix or review artifact unless the user asks for depth.