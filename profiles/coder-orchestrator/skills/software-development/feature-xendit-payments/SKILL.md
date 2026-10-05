---
name: feature-xendit-payments
description: Use when implementing or extracting a Xendit invoice checkout with Go, SQLite, React, authenticated return confirmation, verified webhooks, idempotent fulfillment, and payment recovery.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feature, xendit, payments, webhook, go, sqlite, react]
    related_skills: [payment-integration-hardening, test-driven-development]
---

# Feature: Xendit Payments

## Overview

Implement Xendit as a state machine, not a redirect button. Checkout persists immutable intent before provider creation; webhook and return confirmation reconcile against provider truth; one transaction finalizes payment and fulfillment exactly once.

Load only the templates matching the project stack. Replace placeholders; never copy demo identities or secrets.

## Configuration

Required backend environment:

| Variable | Purpose |
|---|---|
| `XENDIT_SECRET_KEY` | Server-only API key |
| `XENDIT_CALLBACK_TOKEN` | Server-only callback token |
| `XENDIT_MODE` | Explicit `test` or `live` mode |
| `PUBLIC_BASE_URL` | Canonical public API origin |
| `WEB_APP_URL` | Canonical public frontend origin |
| `DATABASE_URL` or `SQLITE_DB_PATH` | Database location |

Optional:

| Variable | Purpose |
|---|---|
| `API_BASE_PATH` | API mount prefix; normalize once |
| `PUBLIC_PATH` | Frontend mount prefix; normalize once |
| `PAYMENT_RECOVERY_INTERVAL` | Bounded reconciliation interval |
| `VITE_USD_TO_IDR_RATE` | Display-only rate; server quote remains authoritative |

Do not introduce aliases in new systems. `XENDIT_SECRET` and `XENDIT_WEBHOOK_TOKEN` are legacy names found in source history, not recommended names.

Provider dashboard callback URL: `${PUBLIC_BASE_URL}${API_BASE_PATH}/api/v1/payments/xendit/webhook`. Success/failure URLs must use `WEB_APP_URL` and the exact frontend mount path. Test exact generated URLs.

## End-to-end flow

1. **Quote:** server validates package/cart and returns authoritative amount, fee, currency, and quote inputs.
2. **Stable attempt:** frontend generates one non-secret idempotency key for a logical intent and reuses it across retries. A changed package/session/cart creates a new key.
3. **Persist intent:** transaction creates a pending purchase and immutable item/benefit snapshots before contacting Xendit. A unique `(buyer_id, client_idempotency_key)` constraint is mandatory.
4. **Create or adopt invoice:** query Xendit by stable `external_id`; validate and adopt an existing invoice before creating. Persist invoice ID, URL, deadline, and lifecycle.
5. **Redirect:** allow only HTTPS Xendit invoice hosts; use same-tab navigation.
6. **Confirm:** owner-scoped return endpoint reconciles with Xendit. UI begins at “Confirming payment,” never success.
7. **Webhook:** constant-time callback-token check, then fetch provider invoice. Treat payload as a wake-up signal, not truth.
8. **Finalize:** conditional pending-only transition + finalization ledger + all benefits + notification/audit in one DB transaction.
9. **Recover:** worker runs once at startup and periodically; retries transient failures and resumes unfinished purchases.

## State model

Payment status: `pending | paid | failed | cancelled | expired | refunded`.

Invoice creation is separate: `creating | created | invoice_creation_failed`. A provider timeout or local persistence error does not mean payment failed.

Provider `PENDING` outranks a local elapsed clock. Locally expire only when a trustworthy provider deadline exists, there is no usable provider invoice identity, and the deadline elapsed.

## Security invariants

- Fetch provider state and match invoice ID, external ID, exact amount, currency, and status.
- Scope confirmation and resumable invoice URLs to the authenticated owner.
- Never expose invoice URLs in admin/public DTOs.
- Derive payer identity from the authenticated buyer; never use fixed demo identity.
- Keep provider credentials server-side; frontend receives only invoice URL and public status.
- Any stub webhook requires multiple development/test gates and must refuse startup in production.
- Use database uniqueness and conditional updates; UI button disabling is not idempotency.

## Templates

- `templates/env.example` — configuration contract.
- `templates/schema.sql` — minimal SQLite state, snapshots, and finalization ledger.
- `templates/checkout-client.ts` — stable intent key and invoice URL validation.
- Backend adapters, handlers, recovery worker, return page, and focused tests must be copied only after adapting the source patterns described in `references/implementation-checklist.md`; do not invent framework glue.
- `references/implementation-checklist.md` — schema, routes, dashboard setup, deployment, and verification.

## Pitfalls found in real implementations

1. Callback status was trusted without provider verification.
2. Count-then-insert fulfillment duplicated benefits under concurrency.
3. Retrying an ambiguous create produced duplicate invoices.
4. Xendit succeeded but local invoice persistence failed; retry must adopt by `external_id`.
5. A fresh key per click defeated idempotency.
6. Missing `crypto.randomUUID` crashed before checkout POST; use a compatibility fallback only for deduplication, never secrets.
7. UI showed success before backend confirmation.
8. Failure routes mixed purchase and package identifiers.
9. Preview mount paths produced incorrect provider-issued URLs.
10. Mutable package definitions changed fulfillment after purchase.
11. Resume URLs leaked through broad DTOs.
12. Historical and current callback-token environment names drifted.

## Verification checklist

- [ ] Missing/wrong callback token rejected.
- [ ] ID, external ID, amount, currency, and provider-status mismatches rejected.
- [ ] Duplicate and concurrent callbacks fulfill exactly once.
- [ ] Mid-finalization failure rolls back status, ledger, benefits, notification, and audit.
- [ ] Ambiguous create and post-create persistence failure adopt the existing invoice.
- [ ] Same key + changed intent is rejected; same key + same intent replays safely.
- [ ] Return page never displays premature success and redirects only after verified paid.
- [ ] Worker runs immediately and periodically; transient errors remain retryable.
- [ ] Exact public callback/success/failure URLs work through the deployed mount path.
- [ ] Authenticated public E2E reaches a genuine Xendit test invoice and verifies the buyer’s resulting entitlement.

## Provenance

Extracted from the production-shaped Go/SQLite and React implementation in Komuna (`api/v1/commerce_handlers.go`, `api/v1/push_jobs.go`, `api/v1/schema.go`, `apps/web/src/pages/CheckoutPage.tsx`, and `PaymentReturnPage.tsx`). Historical Worker code is not the serving-source template.
