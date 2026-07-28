# Payment resume and expiry verification

Use this checklist when a purchase UI lets a customer resume an unpaid provider invoice or when stale pending purchases become expired.

## Security boundaries

- Return resumable invoice URLs only from an authenticated, owner-scoped purchase endpoint.
- Use separate member and admin DTOs. Do not reuse the owner DTO for admin/program listings; regression-test that admin JSON omits `invoice_url`.
- Treat the invoice URL as a bearer-like payment capability even if an administrator can otherwise view the purchase.
- Render **Complete payment** only when status is `pending`, the URL passes an explicit provider-host/scheme allowlist, and a valid known deadline has not elapsed.
- Open external payment URLs with `rel="noopener noreferrer"`.
- Resume the existing provider invoice; the action must not call checkout or create another purchase/invoice.

## Expiry semantics

- Provider truth wins: `PAID` fulfills, `EXPIRED` becomes a distinct `expired` status, `PENDING` stays pending, and transient network/provider failures stay pending for retry.
- Do not infer expiry from record age. Local expiry is acceptable only when a trustworthy provider deadline is stored and has elapsed and there is no usable provider identity to query.
- Hide the resume action immediately when a valid stored deadline is in the past, even if periodic reconciliation has not yet changed the database status. Show stale/expired guidance instead.
- Preserve `expired` through schema constraints/migrations, API filters/counts, admin views, and member/profile views. Exclude expired attempts from completed-purchase and spending totals.

## Reliability verification

- Exercise callback authentication, provider identity/amount/currency checks, pending-only state transitions, atomic/idempotent fulfillment, duplicate/concurrent callbacks, and missed-webhook reconciliation.
- Test ambiguous invoice creation: if the provider created an invoice but the response or local persistence failed, retry must first find and validate by `external_id`, adopt it, and avoid a second provider POST.
- Confirm the reconciliation scheduler actually starts, runs periodically, and uses the same canonical finalization path as webhooks.
- For snapshot-backed previews, run the preview API against a copied database and never production data. Remember that an immediate reconciliation scheduler can mutate the snapshot at startup; this is acceptable only in the isolated preview.

## UI cases

Test pending with valid URL/deadline, pending with invalid URL, pending with elapsed deadline, missing deadline, paid, failed, expired, and missing purchase ID. Success UI must remain neutral until the backend verifies paid status.
