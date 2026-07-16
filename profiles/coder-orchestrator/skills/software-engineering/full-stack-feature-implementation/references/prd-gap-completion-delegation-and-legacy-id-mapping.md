# PRD gap completion: delegated scope, legacy mappings, and live smoke

Use this when completing an approved PRD in an existing compact Go + SQLite + React app, especially when a new domain model must coexist with legacy scheduler tables.

## Workflow

1. Translate each approved requirement into a thin vertical slice: schema, authenticated API, UI, focused test, and public smoke.
2. After delegated work returns, inspect the actual diff and search for every acceptance marker. Do not accept a worker summary as evidence that the slice is complete.
3. Run the full project gates in the parent agent. Then perform a live API smoke that creates the new entity chain from a fresh account; build success alone will not expose persisted-ID or migration collisions.
4. If new entities mirror legacy runtime entities, use an explicit mapping foreign key. Never assume independent SQLite `INTEGER PRIMARY KEY` sequences can share IDs.
5. Route all compatibility operations through that mapping: child creation, updates, deletion checks, scheduler joins, effective working directory, and cleanup.
6. Add a regression test that starts with pre-existing legacy rows, creates the new entity, asserts distinct IDs are allowed, and verifies work is routed to the mapped legacy row.
7. Rebuild the embedded frontend before the Go binary, deploy, restart, and repeat the public fresh-account smoke.
8. Inspect Git history/status before final commit. Delegated agents may have committed despite being told not to; report and preserve intentional commits rather than accidentally squashing or misrepresenting them.

## Minimal mapping pattern

```sql
ALTER TABLE columns ADD COLUMN lane_id INTEGER REFERENCES lanes(id);
CREATE UNIQUE INDEX IF NOT EXISTS columns_lane_id_uq ON columns(lane_id);
```

For a fresh column, create the legacy lane first, read its generated ID, then insert the column with `lane_id`. For existing rows, perform a guarded backfill only where an ownership-compatible legacy row exists.

## Verification checklist

- Existing database opens and legacy data remains.
- Fresh account can create workspace → board → column.
- Generated column names and optional-worktree behavior survive API round trips.
- A column can be created when the account already has default legacy lanes.
- Jobs created through the column API store the mapped legacy lane ID.
- Scheduler resolves custom argv and workspace/worktree cwd through the mapping.
- Go tests, race test, vet, frontend tests/build, service health, public assets, and live API smoke pass.

## Pitfalls

- **Schema presence is not feature completion:** tables without CRUD, scheduler wiring, and UI do not satisfy a PRD slice.
- **Shared numeric IDs are brittle:** `INSERT INTO lanes(id=column_id, ...)` collides as soon as either table has pre-existing rows.
- **Worker self-reports are unverified:** inspect files and rerun commands in the parent context.
- **HTTP 200 is too weak:** exercise the complete creation chain and inspect returned fields.
