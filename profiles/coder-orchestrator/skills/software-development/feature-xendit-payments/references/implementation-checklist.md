# Xendit implementation checklist

## Provider setup

1. Create separate Xendit test/live credentials.
2. Configure the invoice callback URL as `${PUBLIC_BASE_URL}${API_BASE_PATH}/api/v1/payments/xendit/webhook`.
3. Store `XENDIT_SECRET_KEY` and `XENDIT_CALLBACK_TOKEN` only in server secret storage.
4. Validate credentials with a read-only query; never create an invoice merely to test a key.

## Backend routes

- `POST /checkout/quote`: authenticated, validates purchasability and calculates authoritative totals.
- `POST /checkout`: authenticated, requires an idempotency key, stores intent/snapshots, then creates or adopts an invoice.
- `POST /checkout/confirm`: authenticated and owner-scoped; reconciles provider state and returns a server-owned destination.
- `POST /payments/xendit/webhook`: public but callback-token authenticated; payload only identifies the invoice to reconcile.

## Create/adopt algorithm

1. Insert or load purchase by `(buyer_id,idempotency_key)`.
2. Compare the stored intent hash; conflict on a changed intent.
3. If invoice identity is missing, query Xendit by `external_id=purchase_id`.
4. Validate any candidate’s external ID, amount, and currency; adopt it.
5. Only if no matching invoice exists, create one with exact success/failure/callback URLs.
6. Persist provider identity and deadline. If this write fails, leave the purchase recoverable; the next retry repeats step 3.

## Webhook/confirmation reconciliation

Fetch the invoice from Xendit and compare invoice ID, external ID, integer minor-unit amount, currency, and status. Finalization uses a conditional `pending -> paid` update and inserts the finalization ledger and all entitlements in the same transaction. Duplicate callbacks return success after observing prior finalization.

## Recovery

Run recovery once at startup and on a bounded ticker. Claim a limited batch of retryable purchases. Use backoff through `retry_count/next_retry_at`; transient network/provider failures stay pending. Preserve explicit provider terminal states.

## Frontend

Generate one key per stable logical intent. Fetch quote before enabling Pay. Validate invoice URL host before same-tab navigation. The return page starts neutral, calls owner confirmation, renders pending/failure/error distinctly, and redirects only after verified paid.

## Minimum tests

Token rejection; provider-field mismatches; same-key replay and changed-intent conflict; concurrent callbacks; rollback injection; ambiguous create adoption; persistence-failure adoption; immutable snapshots; scheduler startup/repeat; provider-pending precedence; exact mounted URLs; owner-only confirmation/URL; missing `crypto.randomUUID`; authenticated public Xendit test-invoice E2E.
