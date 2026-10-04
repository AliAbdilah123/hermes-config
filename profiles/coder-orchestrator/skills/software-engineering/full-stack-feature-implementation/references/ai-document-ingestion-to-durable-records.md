# AI document ingestion through durable domain records

Use for receipt, invoice, statement, or similar image/PDF ingestion where success means durable business records—not merely a parsed draft.

## Trace both pipelines completely

For each document type, map:

1. UI file acceptance and ordering.
2. Authenticated upload boundary and size/content checks.
3. Provider request construction and model/runtime configuration.
4. Runtime validation of provider JSON.
5. Human review/edit state.
6. Atomic persistence into the canonical domain tables.
7. Reload/read-back proving the records exist.

A document marked `finalized` is not proof that an expense or transaction was created. Inspect the final handler for inserts into the canonical table and any child rows.

## Minimal reliable server design

- Keep provider credentials server-side; do not require browser-managed API keys when a configured backend gateway exists.
- Accept provider base URLs and normalize them once at the shared request boundary. If configuration may be a `/v1` base, append `/chat/completions`; if it is already the full endpoint, leave it unchanged.
- Validate AI output at runtime: required strings, date format, allowed enum values, finite positive amounts, arrays, and item fields. TypeScript casts are not validation.
- Return sanitized provider failures to users; do not expose upstream bodies or credentials.

## Durable receipt finalization

Finalize in one DB transaction:

1. Lock/read an owned receipt in the reviewable state.
2. Validate its edited extraction.
3. Resolve an owned active wallet/account.
4. Insert the canonical transaction.
5. Insert line items.
6. Link the transaction to the source receipt with a unique nullable source ID/index.
7. Mark the receipt finalized.
8. Commit, then recalculate derived balances.

A repeated finalize must conflict or return the existing result; it must never create a second transaction. Validation failure must leave the receipt reviewable and create zero transactions.

## Durable statement import

- Put the entire row batch in one DB transaction; row N failure must roll back rows 1..N-1.
- Check wallet/account ownership server-side. Client-selected IDs are untrusted.
- Prefer explicit DTO/column allowlists over turning arbitrary JSON keys into SQL identifiers.
- Treat duplicate detection as advisory unless an import/source idempotency key exists; date+amount+type can both miss duplicates and flag legitimate repeats.
- Verify the returned insert response, then query the canonical records again after import.

## Tests and live verification

Tests should first fail for:

- `/v1` base URL normalization.
- Finalize creates one transaction plus children.
- Second finalize creates no duplicate.
- Invalid extraction rolls back.
- Mixed-validity statement batch is atomic.
- Foreign wallet/account IDs are rejected.

After unit/build checks, exercise authenticated deployed routes with real representative images and the configured provider. Confirm processing reaches review-ready, finalize/import succeeds, and a fresh read returns exact expected record counts. If browser automation is unavailable, authenticated public HTTP is valid API-level evidence, but report that rendered browser interaction remains unverified.

Never commit runtime secrets. Update ignored protected environment files, restart, inspect only variable names/sanitized endpoint/model, and scan the staged diff for the secret before commit.