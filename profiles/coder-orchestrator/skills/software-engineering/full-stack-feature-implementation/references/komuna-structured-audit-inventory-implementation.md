# Komuna structured audit inventory implementation

Use this playbook when an approved audit-action inventory must be implemented across Komuna's Go + SQLite mutation handlers and React audit UI.

## Core pattern

1. Add a nullable/defaulted `details` JSON text column to `audit_logs`; preserve existing rows and API compatibility.
2. Add `details` to the Go DTO/scanner/query and frontend API type.
3. Introduce one small audit writer accepting an `Exec`-compatible interface so both `*sql.DB` and `*sql.Tx` can use it.
4. Marshal structured details centrally. Never include passwords, hashes, tokens, payment secrets, or unnecessary personal data.
5. Resolve actor identity consistently; genuine provider/system events may use a system actor, but ordinary mutations should retain the authenticated user.
6. Write the audit event in the same transaction as the business mutation whenever a transaction already exists. Treat audit failure as transaction failure where losing the event would violate the append-only contract.
7. For non-transactional handlers, emit only after checking that the mutation succeeded and, for conditional updates, that `RowsAffected() > 0`.

## Event design

- Use stable dotted keys: `product.created`, `member.banned`, `purchase.paid`.
- Record one event per successful business state transition, not per SQL row or retry.
- Put searchable identity in actor/target columns and contextual data in `details`.
- Include old/new values when cheaply available, plus amounts, counts, references, and reasons.
- Aggregate purchase completion into one `purchase.paid` event containing buyer/package, base amount, fee, total, safe payment reference, and voucher/subscription counts. Do not emit one dashboard event per generated voucher.
- Guard payment callbacks against duplicate `purchase.paid` and `purchase.failed` events.
- For versioned immutable packages, distinguish `package.created` from `package.version_created`, then audit archival of the superseded package.

## Adjacent-flow rule

An audit event must never claim a transition that the handler does not persist. Before wiring request-decision events, verify the business mutation itself:

- Join-request approval must update the request and activate the pending membership.
- Booking-request approve/deny must persist request status and resolution time.

Fix these flows transactionally before adding their audit records.

## TDD slices

Write focused failing tests by mutation family rather than one enormous end-to-end fixture:

1. Structured details round-trip and writer support for transactions.
2. Request-decision persistence plus audit.
3. Representative member mutation and exactly-once behavior.
4. Product/package/voucher actions.
5. Session/booking/attendance actions.
6. Purchase aggregation and callback deduplication.
7. Frontend details rendering and API error-state compatibility.

Run each focused test to observe RED, then run `go test ./...`, the focused Audit Log frontend test, and the production web build.

## Frontend

Render structured details as secondary readable information without replacing the existing action, actor, target, and reason columns. Keep older rows with absent details valid. If a Vitest module mock hides a real exported error class used by the page, use a partial mock that imports and spreads the actual module before overriding API calls.

## Deployment verification

1. Build the Go binary at the path used by the systemd service.
2. Restart and verify the actual configured listen address, then public `/api/v1/health`.
3. Build Vite with deprecated auth-provider environment variables removed.
4. Deploy the clean `dist/` directory to the nginx-served Komuna path.
5. Verify public index asset hashes and a details-rendering marker in the deployed bundle.
6. Commit and push only the intended tracked source/tests; do not sweep unrelated untracked review artifacts or database backups into the commit.
