# Xendit + Go + SQLite checklist

- Xendit invoice callbacks use the documented static `x-callback-token`; do not substitute an invented HMAC scheme.
- Verify a callback by fetching the invoice and matching invoice ID, `external_id`, IDR amount, currency, and paid-like status.
- Use an HTTP client with explicit total/transport timeouts.
- In SQLite, make fulfillment transactional and use unique rows for purchased-entry units or a fulfillment ledger; `COUNT(*) == 0` is not concurrency-safe.
- Snapshot package-entry product, benefit type, quantity, and validity when checkout starts.
- Subscription quantities should be constrained to one unless the product defines multi-subscription semantics.
- Distinguish `invoice_creation_failed` from payment pending. On retry, search Xendit by `external_id` and adopt a validated existing invoice before creating another.
- Provider `REFUNDED` must not fall through to pending or paid. Only implement `paid -> refunded` when entitlement revocation/consumption policy is explicit.
- Failure redirect paths must use the package identifier expected by the checkout route, not the purchase ID.
- Safe credential validation: authenticated read-only invoice listing/query with a guaranteed nonexistent external ID; never create an invoice merely to test a key.

Suggested focused test regex: payment, webhook, checkout, subscription, recovery, Xendit, and idempotency. Still run broad checks, but compare failures against a clean baseline before assigning blame.