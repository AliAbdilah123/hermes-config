# Komuna Package Purchase → Automatic Session Booking

Use when a member attempts to book a session without an eligible voucher, buys a matching package, and should have the original session booked automatically after payment.

## Core architecture

Treat this as one durable server-owned workflow, not a chain of browser-only redirects:

1. Booking UI sends the exact intended `sessionId` into package checkout.
2. Checkout validates that the session belongs to the package's program and that a package entry covers the session product.
3. Persist the intended session on the purchase (a nullable `intended_session_id` is sufficient).
4. After confirmed payment issues vouchers/subscriptions, the payment-completion path invokes shared idempotent booking logic.
5. Return booking outcome separately from payment outcome.

This survives external payment redirects, browser closure, delayed webhooks, refreshes, and duplicate provider callbacks.

## Removing the join-first gate safely

Removing the frontend membership modal is insufficient because purchases and benefits are keyed through `program_members`.

At authenticated checkout, resolve membership transactionally:

- reuse an active basic membership;
- reactivate an allowed `inactive`/`left` membership;
- create one basic member row if absent;
- reject banned users and preserve private/invitation-only policy;
- never grant admin or manager roles;
- create the purchase against the resolved member in the same transaction.

Signed-out users still authenticate before payment. The feature removes only the requirement to manually join first.

## Shared booking helper

Extract manual claim creation into one helper used by both `POST /claims` and payment completion. Preserve:

- existing active-claim detection;
- session status, time, and capacity checks;
- same-program and matching-product checks;
- FIFO active voucher selection;
- product-scoped and program-wide subscription fallback;
- conditional voucher/session updates;
- claim creation and audit events.

For auto-booking, `already_booked` is an idempotent success outcome. Manual HTTP behavior may retain its existing conflict response.

## Payment and booking are separate outcomes

A paid purchase must remain paid if the session becomes full, ends, is cancelled, or otherwise cannot be booked. Return structured fields such as:

- `booking_status`: `booked | already_booked | failed | not_requested`
- `booking_claim_id`
- `booking_error`
- context-aware `redirect_url`

Never show “payment failed” for a successful payment followed by an unsuccessful booking. Keep issued benefits available and direct the user back to the intended session/program with a truthful explanation.

## Security and validation

The server must verify:

- purchase ownership;
- session and package share a program;
- purchased package grants an entitlement for the session product;
- the session remains bookable at completion;
- retries cannot consume another voucher or create a second active claim.

Query-string `sessionId` may support display/navigation, but the purchase row is the source of truth and the browser must not perform the post-payment claim independently.

## Minimality ceiling

Prefer one nullable purchase column plus a shared booking helper. Do not add a booking-intent table, queue, background worker, or frontend global state unless production evidence requires asynchronous retries or multiple intents per purchase.

## Required tests

- authenticated non-member checkout creates/reactivates only a basic membership;
- banned/private-policy cases remain blocked;
- valid intent persists; wrong-program and package-product mismatch fail before invoice creation;
- voucher and subscription purchases each auto-book once;
- duplicate webhook/confirmation remains one claim and one consumed voucher;
- no intent preserves ordinary Wallet behavior;
- session full/cancelled after payment keeps purchase paid and reports booking failure;
- frontend checkout carries the exact session ID and shows no join-first modal;
- real return and local/stub completion render the same truthful booking outcome.
