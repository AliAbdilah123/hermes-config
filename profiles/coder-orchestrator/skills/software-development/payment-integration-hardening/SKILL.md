---
name: payment-integration-hardening
description: Secure and verify provider-backed checkout, webhook, reconciliation, entitlement fulfillment, and payment-return UX.
version: 1.0.0
metadata:
  hermes:
    tags: [payments, webhooks, idempotency, fulfillment, reconciliation]
---

# Payment Integration Hardening

Use when auditing or implementing payment-provider checkout that grants digital benefits, subscriptions, vouchers, bookings, or products.

## Core workflow

1. Identify the implementation that actually serves production; provider code elsewhere in the repository is not evidence.
2. Inspect runtime mode and credentials with values masked. Validate credentials using a safe read-only provider request.
3. Trace checkout → provider invoice → webhook/return confirmation → local status transition → fulfillment → wallet/order display.
4. Write failing tests before each behavior change, including concurrency and partial-failure cases.
5. Keep test/live mode and application-flow activity as separate conclusions.

## Safety invariants

- Authenticate callbacks using the provider’s documented mechanism and constant-time comparison where applicable.
- Never trust callback status alone. Fetch/correlate provider invoice ID, external purchase ID, exact amount, currency, and provider status.
- Enforce legal transitions with conditional SQL; stale callbacks cannot downgrade paid purchases.
- Put status transition, all entitlement inserts, fulfillment marker, and audit record in one DB transaction. Check every DB error.
- Use DB-backed idempotency for checkout and fulfillment. Never rely on UI button disabling or count-then-insert.
- Snapshot purchased package entries at checkout; fulfillment must not reread mutable package definitions.
- Webhook, return-page confirmation, and scheduled recovery call one canonical finalizer.
- Transient provider failures remain retryable; explicit provider terminal states stay distinct (`expired` is not generic `failed`). A reconciliation worker must actually start, run immediately, and repeat on a bounded interval.
- Provider truth wins for expiry. Keep provider-backed `PENDING` pending; use local expiry only when a trustworthy stored provider deadline exists, no usable provider invoice identity exists, and that deadline has elapsed.
- Return UX starts neutral (“Confirming payment…”), handles missing/pending/failure/error, and redirects only after verified paid.
- Member purchase history should explain incomplete payment, show the provider deadline when available, and offer a resume action only for an existing valid pending invoice. Never create a new purchase from that action.
- Resumable invoice URLs are bearer-like secrets: expose them only through an ownership-scoped member endpoint, never public or admin/program purchase listings. Separate member and admin DTOs to make accidental leakage harder.
- Hide resume actions for paid, failed, refunded, expired, invalid-host, and valid-but-elapsed invoices. Open external provider URLs with `noopener noreferrer` and an explicit host allowlist.

## Pay-click failures before checkout reaches the API

When clicking Pay fails immediately and server logs show the quote request but no checkout request:

1. Treat the provider and backend as downstream until browser evidence proves the checkout POST occurred.
2. Inspect synchronous code executed before the request: idempotency-key generation, query parsing, auth/session reads, analytics, and payload construction.
3. Capture browser `pageerror` plus quote and checkout responses. A successful quote followed by no POST strongly indicates a client-side exception.
4. Audit modern Web APIs used in the click handler, especially `globalThis.crypto.randomUUID()`. A polyfill that only runs when `crypto` exists does not protect contexts where `crypto` itself is absent.
5. Keep one stable idempotency key per logical attempt, but generate it through a compatibility-safe helper. Prefer native `crypto.randomUUID`; use a sufficiently unique fallback only for request deduplication, never for secrets or authentication.
6. Add a regression test that removes the Web API, clicks Pay, and asserts the checkout POST contains a non-empty idempotency key.
7. Public E2E should deliberately disable the API before clicking Pay, require checkout `200`, and verify navigation to the genuine provider test/staging invoice URL.
8. Do not stop at the failure boundary or likely root cause. Continue through regression test, fix, deployment, and authenticated public provider-invoice E2E unless concretely blocked; do not require the user to say “Continue.”

## Critical ambiguous-create rule

If the provider may have created an invoice but the response was lost, malformed, timed out, or failed to persist locally, a retry must first query the provider by the stored external purchase ID. Validate and adopt a matching invoice before attempting creation again. Do not guess unsupported idempotency headers.

## Verification matrix

- missing/wrong callback token rejected;
- mismatched ID, amount, or currency rejected;
- duplicate/concurrent callbacks issue exact benefits once;
- forced mid-fulfillment failure rolls back everything;
- late failure cannot downgrade paid;
- lost webhook reconciles exactly once;
- provider `EXPIRED` persists and renders as Expired in admin and member purchase views;
- transient provider errors leave the purchase pending;
- member resume link appears only to the owner for a valid, unelapsed pending invoice;
- admin/public purchase JSON contains no resumable invoice URL;
- repeated/concurrent checkout creates one purchase/invoice;
- ambiguous create retry adopts the existing provider invoice;
- archived/empty/invalid package creates no purchase;
- mixed package fulfills all entries or none;
- return page never shows premature success.

## Evidence and reporting

Report targeted checks separately from baseline suite/lint failures. Compare the same broad command on a clean baseline before calling failures regressions. For nontechnical stakeholders, lead with a short verdict and a concise `Problem | Solution` table; keep state-machine and SQL detail optional.

See `references/xendit-go-sqlite.md` for a concrete Xendit/Go/SQLite checklist, `references/pending-expiry-and-resume.md` for provider-truth expiry, reconciliation scheduling, owner-only invoice links, and purchase-surface tests, and `references/preview-safe-local-checkout.md` for explicitly gated providerless preview checkout, strict TDD, public-chain gates, and verification-script hygiene.