# Xendit Payment Hardening and Preview Gates

Use when auditing or changing Komuna's active Go/SQLite Xendit checkout. The TypeScript/Worker implementation may be stronger but is not runtime evidence.

## Audit boundaries

Verify all three separately:

1. **Provider/runtime:** inspect the running unit, effective masked environment, active binary, and make only a read-only Xendit probe. Distinguish valid credentials, test/live mode, and whether checkout actually calls Xendit.
2. **Backend:** trace checkout creation, webhook authentication, provider correlation, state transitions, fulfillment, retries, and refund behavior in the active Go API.
3. **UX:** inspect checkout and return states. Never perform a real charge during an audit unless explicitly authorized.

## Minimum safe payment contract

- Require and constant-time compare Xendit's `x-callback-token` on every webhook alias.
- Never trust callback status alone. Fetch/correlate the provider invoice and validate invoice ID, external purchase ID, exact amount, currency, and provider status.
- Enforce legal transitions with conditional SQL. Normal terminal processing is `pending -> paid|failed`; do not permit late callbacks to downgrade paid purchases.
- Finalize status, all entitlements, fulfillment ledger, and audit record in one DB transaction. Check every SQL/scan/rows error.
- Make fulfillment DB-idempotent, not `COUNT`-then-insert. Use durable unique keys for purchase-entry/unit fulfillment and make duplicate callbacks return the existing result.
- Snapshot package entries at purchase creation. Fulfillment must not reread mutable package definitions.
- Reject archived, empty, inactive-product, invalid-quantity packages before creating a purchase. Constrain subscription quantity to its actual semantics (currently exactly one).
- Scope confirmation to the purchase owner. Webhook authentication and member confirmation ownership are separate controls.
- Use one canonical reconciliation/finalization path for webhook, return-page confirmation, and recovery jobs. Transient provider errors remain recoverable; only explicit terminal provider states become failed.
- Keep provider calls bounded by HTTP timeouts.

## Checkout idempotency and ambiguous invoice creation

Client button disabling is UX only. Require a client idempotency key and a member-scoped unique DB constraint. Repeated or concurrent requests must return the existing purchase/invoice.

A timeout is ambiguous: Xendit may have created the invoice while Komuna lost the response or failed to persist it. Before any retry POST:

1. Query Xendit by the purchase `external_id`.
2. If found, validate external ID, amount, currency, provider ID, and hosted URL.
3. Persist/adopt that invoice and return it.
4. If lookup errors or returns mismatched data, fail closed; do not create another invoice.
5. POST a new invoice only when the lookup conclusively shows none exists.

Regression tests should simulate both response loss and local invoice-persistence failure and assert provider POST count remains exactly one across retries.

## Truthful return UX

- Initial state: **Confirming payment…**
- Show and redirect as success only after verified `paid`.
- Pending remains pending with safe retry guidance.
- Missing purchase ID is an invalid-link state, never success.
- Failed and provider/network errors must not start a success countdown.
- Avoid duplicate independent confirmation/countdown flows between return page and Wallet.

## Refund boundary

Do not invent entitlement revocation when provider refunds and business policy remain stubbed. Ensure `REFUNDED` is never misclassified as paid or pending, document the unsupported boundary, and implement refunds only with an explicit policy for unused and consumed benefits.

## TDD and verification

Write failing tests first for token rejection, provider mismatch, concurrent callbacks, partial insertion rollback, stale transitions, missed-webhook recovery, checkout retries, ambiguous invoice creation, immutable snapshots, and return-page states.

Report gates separately:

- focused Go payment tests;
- focused React checkout/return tests;
- changed-file lint;
- production build;
- independent security review;
- repository-wide checks, explicitly identifying failures already present on a clean baseline.

Do not weaken production checks to satisfy older tests that assume missing Xendit configuration. Inject a fake invoice creator/provider in tests whose intended assertion is unrelated to provider setup.

## Isolated preview

Payment changes need a snapshot-backed API preview; a frontend preview pointed at production cannot demonstrate unapproved backend behavior.

1. Build from a clean feature worktree.
2. Create the SQLite snapshot with `.backup`, never raw-copy a live WAL database.
3. Run the feature API on an unused loopback port against the snapshot.
4. Add preview-specific API location before the broad SPA location.
5. Inject the preview basename and API base.
6. Ensure root-built HTML asset paths are rewritten to the preview prefix; probe every JS/CSS MIME type because an SPA fallback can return HTML with HTTP 200.
7. Verify root, a deep payment route, API JSON, DOM markers, and absence of false-success text in headless Chromium.
8. Confirm production's asset identity and DB remain unchanged.
9. Push the feature branch, provide the preview URL, and wait for explicit approval before merge/deploy.

### Pending-payment preview fixtures

A pending-payment card cannot be visually verified when reconciliation has already expired every pending row in the snapshot. Seed a fixture only for the named preview account and only in the isolated snapshot, after backing it up.

- Never invent a URL that merely resembles a Xendit hosted-checkout URL. A syntactically valid placeholder can pass frontend validation while sending the reviewer to a nonexistent checkout. If a display-only fixture was mistakenly given such a URL, remove it instead of leaving a misleading resume action.
- If the reviewed action is **Complete payment**, create a genuine Xendit **test-mode** invoice using the fixture purchase ID as `external_id`, with the exact amount/currency and a bounded duration. Persist the returned invoice ID, hosted URL, and expiry into the snapshot.
- When review ends or the user says not to use the test checkout, remove the fixture from the isolated snapshot and best-effort expire the provider invoice through the documented Xendit endpoint. Verify provider status and local removal separately; if provider expiry cannot be confirmed, say so rather than implying the hosted link is disabled.
- Verify provider status is `PENDING`, identity/amount/currency match the fixture, and the hosted URL responds successfully before asking the user to review it.
- Keep the fixture clearly preview-only, avoid real charges, never mutate production, and replace stale fixture invoices rather than presenting them as functional.
- If there is no real provider invoice, hide the completion action and label the fixture display-only instead of attaching a fake link.

## Communication

Give the user a concise table or short bullets: **problem -> solution -> verification**. Lead with whether live payments are safe. Put detailed evidence behind the summary rather than making the first explanation exhaustive.
