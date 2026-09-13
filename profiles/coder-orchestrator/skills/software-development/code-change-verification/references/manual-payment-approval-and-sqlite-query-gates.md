# Manual-payment approval and SQLite query gates

Use this reference when extending an existing gateway checkout with manual transfer, receipt review, and delayed entitlement issuance.

## Verification order

1. Run the narrow manual-payment happy-path test before the broad suite. Require a real multipart receipt upload with the same optional booking-answer semantics as gateway checkout; an omitted or empty answers field must not become an invalid payload merely because multipart form values are strings.
2. Prove the state boundary: submission creates a pending purchase and zero vouchers/subscriptions/bookings.
3. Approve through the real program-scoped review endpoint and prove exactly one entitlement set plus one buyer notification.
4. Repeat approval and exercise concurrent approval attempts. The terminal state must remain single-issued and auditable.
5. Reject, replace the proof through the buyer flow, reload, and approve the replacement.
6. Test disabled methods at both UI availability and API enforcement boundaries.
7. Test receipt authorization, signature/type validation, size limit, generated storage names, and cleanup on database failure.

## Reuse the paid finalizer correctly

Manual approval must not first set `purchases.status='paid'` and then call a gateway finalizer whose guard is `WHERE status='pending'`; that makes the shared finalizer a no-op and tempts duplicate entitlement logic. Prefer one transaction-safe paid-purchase primitive used by both gateway confirmation and manual approval. It should:

- conditionally claim the pending purchase,
- set paid metadata appropriate to the payment method,
- issue snapshots/entitlements and intended booking once,
- record finalization/idempotency state,
- persist reviewer/audit/notification effects consistently.

Keep provider-specific invoice fields optional for manual payments instead of fabricating gateway IDs.

## SQLite single-connection trap

With `MaxOpenConns(1)`, do not run `db.QueryRow` inside a loop while the parent `Rows` remains open. A list endpoint that enriches purchases with payment method or manual status this way may deadlock, silently return zero/default enrichment, or distort unrelated aggregate tests. Select/join the required fields in the original query, or consume and close rows before follow-up queries.

Leave a focused regression that creates a representative manual purchase, sets `db.SetMaxOpenConns(1)`, calls the list endpoint asynchronously, and fails on a short timeout. Restore the connection setting before teardown if the timeout branch must unblock the request. Raising the pool limit is not a fix.

## Baseline failure classification

When a broad suite exposes failures outside the focused feature, rerun the exact failing tests at the recorded clean upstream baseline using the same command, dependency state, and base SHA. Compare exact failing test names and assertions—not only failure totals, especially for asynchronous UI suites. If they reproduce there, report them separately and do not churn unrelated production code. This does not waive focused feature failures: new manual-payment tests and all directly affected checkout/purchase tests must still pass before frontend or preview work proceeds.

## Frontend compatibility and evidence

Payment-method flags added to platform settings may be absent in older API payloads and test mocks during mixed-version deployment. Normalize missing booleans at the API-to-draft boundary to secure product defaults, and test both current and legacy response shapes. Do not let `undefined` flow into form validation or checkbox state.

Keep evidence separated:

- focused feature tests;
- changed-file lint;
- production build/typecheck;
- broad-suite baseline comparison;
- authenticated public E2E.

A green build does not override broad-suite failures, while reproduced baseline lint/test failures do not invalidate independently passing focused feature checks. Repository-wide lint failures should be classified against baseline; do not edit unrelated files merely to manufacture a green global result.
