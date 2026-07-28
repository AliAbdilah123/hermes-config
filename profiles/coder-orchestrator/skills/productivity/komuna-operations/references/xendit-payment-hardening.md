# Xendit payment hardening

Use this checklist when auditing or implementing Komuna payment flows. Keep the user-facing explanation concise: lead with the verdict, then a simple problem → fix table; provide detailed engineering notes only when requested.

## Audit the active path

- Confirm which service/binary is actually running; do not infer deployment from reference TypeScript code.
- Separate credential validity, test/live mode, and whether checkout really calls Xendit.
- Validate credentials with a read-only provider request. Never create an invoice merely to prove authentication.
- Trace checkout → invoice creation → callback/confirmation → purchase transition → voucher/subscription issuance → wallet display.

## Required safety properties

1. **Authenticated callback:** compare `x-callback-token` with the configured token using constant-time comparison.
2. **Provider correlation:** before fulfillment, verify stored invoice ID, external purchase ID, amount, currency, and terminal status against Xendit. Do not trust callback body status alone.
3. **Legal transitions:** enforce conditional transitions such as `pending → paid|failed`; never allow a stale failure to downgrade `paid`.
4. **Atomic fulfillment:** issue every package benefit and finalize payment in one DB transaction. Check every query, scan, and insert error.
5. **Durable idempotency:** use DB uniqueness/fulfillment records, not `COUNT(*) == 0`. Concurrent duplicate callbacks must produce exactly one expected benefit set.
6. **Complete package delivery:** snapshot or ledger each purchased package entry and verify all expected quantities before completion.
7. **Safe reconciliation:** webhook, return-page confirmation, and scheduled recovery must call one canonical finalizer. Transient provider errors stay pending; only explicit terminal provider states fail a purchase.
8. **Checkout validation:** require an active, non-empty package with active products and valid quantities before creating a purchase/invoice.
9. **Request safety:** use bounded HTTP timeouts and checkout idempotency keys; repeated Pay requests return the existing attempt.
10. **Truthful UX:** show “Confirming payment…” first. Show success and redirect only after verified paid; handle pending, failed, missing-ID, and network-error states without an independent countdown race.

## Product semantics

- Voucher entries issue exactly their configured quantity.
- Subscription entries issue the intended scoped entitlement once.
- A simple/physical product represented only by a voucher is not a shipping/order workflow. Say so explicitly; add inventory/order/fulfillment records only when physical delivery is a real requirement.

## Minimum regression set

- Missing/wrong callback token rejected.
- Correct token but mismatched invoice, amount, currency, or external ID does not fulfill.
- Valid paid callback fulfills exactly once.
- Two concurrent callbacks still produce exactly the expected benefits.
- Forced mid-package insert failure rolls back payment and all benefits.
- Late failed callback cannot downgrade paid.
- Missed webhook is recovered once; transient lookup error remains pending.
- Archived, empty, or inactive-product package is rejected before purchase creation.
- Duplicate checkout requests create one purchase/invoice attempt.
- Payment return UI covers confirming, paid, pending, failed, missing ID, and request error.

## Verification discipline

Run commands from the owning module roots (`api/v1` for Go, `apps/web` for frontend). If repository-wide lint/test fails, capture the exact failing assertion, then run changed-file lint and focused regressions separately. Report each boundary honestly; never turn targeted success into a full-suite claim.
