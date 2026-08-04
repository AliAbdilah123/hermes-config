# Preview subpath payment return isolation

Use when a provider-backed preview is mounted below `/previews/<slug>/` while production uses the same host.

## Failure signature

- Provider invoice is genuinely `PAID`.
- Preview purchase remains `pending`, with no entitlements or intended booking.
- Provider success/failure URLs point to host-root production routes.
- The return page therefore calls the production API/database, where the preview purchase does not exist.
- Provider webhooks may also miss the preview because legacy invoice webhooks are often configured at the provider account/sub-account level rather than per invoice.

## Root fix

Construct every provider-facing URL from the preview-aware web-app base, not a production-root public origin:

```go
base := strings.TrimRight(env("WEB_APP_URL", env("PUBLIC_BASE_URL", fallback)), "/")
apiPath := strings.TrimRight(env("API_BASE_PATH", "/api/v1"), "/")
```

Use that base for callback, success, and failure URLs. `WEB_APP_URL` wins because it identifies the exact mounted UI; `PUBLIC_BASE_URL` remains the root-deployment fallback.

## Regression test

Set a root `PUBLIC_BASE_URL`, a subpath `WEB_APP_URL` with a trailing slash, and an `API_BASE_PATH` with a trailing slash. Capture the provider invoice-create body and assert callback, success, and failure URLs all retain the preview prefix with no doubled slash.

## Recovering an already-paid preview purchase

1. Correlate the user's latest browser checkout by timestamp/IP/session with the server's `payment_checkout_started` event. Capture that event's exact `purchase_id` and `user_id`; never start from an older pending purchase or convenient auth fixture.
2. Join the purchase through its program membership to the buyer account. List nearby purchases if necessary and prove which one belongs to the reported attempt.
3. Read that purchase's provider invoice by ID; verify invoice ID, external purchase ID, amount, currency, and paid/settled status all match.
4. Record entitlement/booking counts for this exact purchase and buyer before recovery. A different account's vouchers are irrelevant even when they came from the same package.
5. Preserve the provider-issued return URL as evidence. Inspect both preview and production access logs while replaying that **exact URL**; a production `404 purchase_not_found` proves cross-database routing even if a manually corrected preview URL succeeds.
6. Exercise the normal owner-scoped preview confirmation endpoint or exact browser return page using the actual buyer's authenticated session. Never edit purchase status directly or fake a webhook.
7. Verify local `paid` state, expected entitlements, intended booking, and the actual buyer's wallet/booking UI.
8. Repeat confirmation and prove counts do not increase.
9. Reopen the original provider-issued URL in the actual buyer's authenticated public browser and assert it lands on the intended success destination without the confirmation-error copy. Do not declare READY from provider state or DB counts alone.

## Compatibility recovery for already-issued wrong URLs

The checkout fix only affects newly created invoices. Existing invoices retain their old return URL. If an affected paid invoice is still circulating:

- Prefer a narrowly scoped compatibility redirect keyed to the exact purchase ID (or another unforgeable, ownership-checked recovery route), rather than changing all production payment returns.
- Preserve the complete query string and redirect explicitly to HTTPS when behind a TLS-terminating proxy/CDN.
- Test the redirect at origin and publicly; CDN-cached redirects may temporarily differ from origin.
- Verify an unrelated purchase still follows normal production behavior.
- Remove the compatibility rule when the affected invoice can no longer be revisited.

## Webhook caveat

An invoice request `callback_url` is not proof that a legacy invoice provider delivers there. Verify account/sub-account webhook configuration separately. Return-page confirmation and reconciliation must still recover missed webhooks through the canonical finalizer.
