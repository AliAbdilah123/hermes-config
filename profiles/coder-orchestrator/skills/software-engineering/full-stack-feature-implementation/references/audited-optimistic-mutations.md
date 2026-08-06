# Audited optimistic mutations

Use this checklist for stateful workflow modules where every mutation must be concurrency-safe and append immutable history.

## Mutation contract

1. Require the aggregate's expected `version` on every mutation, including subresources, file metadata, tags, and bulk actions—not only scalar or stage updates.
2. Start one database transaction.
3. Re-check tenant scope, mutation permission, and any assignment target inside the mutation path. Assignment targets must be active workspace members according to the current membership schema.
4. Apply the domain write with an expected-version predicate and increment the aggregate version. Treat zero affected rows as a stale-version conflict.
5. Insert the immutable event/audit row using the same transaction. Never discard audit insertion errors.
6. Commit only after all writes succeed; rollback otherwise.
7. Return the new version so the client can refresh or continue safely.

## Bulk actions

Send an expected version per selected row. Validate every row first, then update and audit every row in one transaction. Any stale, unauthorized, cross-tenant, or invalid row aborts the whole batch. Archive/restore, assignment, priority, and export permissions still need separate policy checks.

## Provider-derived projections

Do not let manual activity types impersonate provider events. For example, a manual activity must not set `client_reply` or project outreach to `replied`; only a validated, linked provider event may do that. Keep manual activity enums allow-listed in both API and UI.

## Regression tests

Prove at minimum:

- stale subresource versions return conflict and write neither domain state nor audit;
- forced audit failure rolls back the domain write;
- bulk updates are version-checked, per-row audited, and all-or-nothing;
- inactive assignment targets are rejected;
- manual provider-only event types are rejected;
- file version creation and its timeline event are atomic.

After fixes, rerun the full test/build gates and send the corrected diff through a fresh independent review rather than trusting the implementing/fixing agent's self-report.
