---
name: sqlite-state-transition-debugging
description: Diagnose and repair SQLite-backed workflow/state transitions that fail because triggers, historical data, migrations, or generic API error masking disagree.
---

# SQLite State-Transition Debugging

Use when a workflow transition (CRM stage, order status, approval state, queue state) returns a generic failure even though the submitted destination and confirmation fields look valid. Also use when relationship state changes unexpectedly—for example, creating a parent silently reparents older children—because stale client IDs and broad SQLite updates can form one cross-layer transition bug.

## Workflow

1. Reproduce the exact transition sequence and inspect the complete API response.
2. Trace every SQL statement in the transaction, including history/event writes.
3. Inspect SQLite triggers and constraints on every mutated table; generic handler errors often mask trigger messages.
4. Compare the failing runtime row with a freshly created passing row.
5. Review the migration that introduced the invariant and check whether it repaired historical rows.
6. Reproduce the upgrade path from the oldest relevant schema before editing.
7. Fix the invariant mismatch at the data-migration boundary. Keep valid triggers intact and avoid endpoint-specific bypasses.
8. Add one current-row transition regression and one historical-schema upgrade regression.
9. Verify the runtime migration version and repaired row, then exercise the authenticated public browser transition and assert both response and persisted state.

## Principles

- Backfill only rows that otherwise satisfy the trigger's invariant.
- Derive missing technical timestamps from existing deterministic timestamps; do not invent business facts.
- Keep public errors safe, but preserve/log enough internal detail to identify the SQL boundary.
- A health check, build, or local handler test is not public transition evidence.
- For cross-tenant production E2E, use a dedicated temporary identity with minimum membership; never alter the reported user's credentials.

## References

- See `references/historical-row-trigger-failures.md` for the diagnostic recipe, migration shape, and verification matrix.
- See `references/stale-dialog-state-reparenting.md` for tracing reusable create/edit dialog state through relationship-ID payloads into destructive `parent_id` updates.
- See `references/reparented-children-hidden-by-status-filters.md` when repaired children exist in SQLite/API but disappear because top-level and nested UI filters leave them no visible location.
