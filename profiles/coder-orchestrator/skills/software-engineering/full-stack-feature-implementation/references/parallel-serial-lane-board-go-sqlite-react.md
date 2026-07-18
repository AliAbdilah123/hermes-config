# Parallel serial-lane boards in Go + SQLite + React

Use when Projects act as Boards, Columns are independent execution lanes, and Jobs within each Column execute serially from top to bottom.

## Reuse-first domain mapping

Prefer extending existing entities rather than creating parallel models:

- Project → Board
- Delegated status/lane entity → Column
- Task → Job
- Task messages → full Job conversation

Keep Job status separate from Column identity. A Column is an ordered queue, not a workflow-status bucket.

## Minimal schema

- Project: nullable/empty `default_workspace`.
- Column: `project_id`, optional identifier/name, `order_index`, and archive flag/timestamp.
- Job: `column_id` and stable `lane_position`.
- Tenant/user settings: provider name (default `hermes`), URL, secret, and model.

A new Board should insert only the Project row and therefore have zero Columns.

## Required API invariants

- Validate every Project, Column, and Job ID against the authenticated tenant.
- Column creation must reject missing or foreign `project_id`.
- Job creation must reject blank titles and append at the lane tail deterministically.
- Reorder in one transaction; accept only the complete ordered set of todo Job IDs for that Column. Reject running/completed jobs, missing IDs, duplicates, foreign IDs, and cross-Column IDs.
- Archiving a Column removes it from active Board and scheduler queries without deleting history.
- Project create and edit both persist `default_workspace`; validate it as an absolute path at the trust boundary, with execution-time allowed-root checks before use.
- Provider reads return only `has_secret`; never return the secret. A blank secret update retains the saved value.
- Validate provider URLs as absolute HTTP(S) URLs.

## UI behavior

- Empty Board visibly retains Add Column.
- Each active Column has Archive and a bottom Add Job form.
- Jobs render by `lane_position`.
- Only todo Jobs expose reorder controls. Native up/down controls are a dependency-free, keyboard/mobile-safe baseline; drag-and-drop can be added later without removing them.
- Clicking a Job opens one shared accessible Dialog containing details and the full conversation. Reuse the existing message-posting flow rather than duplicating it inside cards.
- Project create and edit forms both expose Default workspace.
- Settings exposes provider, URL, write-only secret, and model.

## Execution semantics

Persisted ordering is not an executor. Do not claim Jobs run automatically unless a real scheduler exists.

For a real scheduler:

1. Atomically claim at most the first runnable Job in each active Column.
2. Prevent a second running Job in the same Column.
3. Execute claimed Jobs from different Columns concurrently.
4. Perform provider network calls outside the SQLite claim transaction.
5. Persist terminal outcome before the next Job in that Column becomes eligible.

## Restart-safe SQLite migrations

Some small apps execute every migration file on every startup without a migration-history table. Multi-statement `ALTER TABLE ... ADD COLUMN` files are dangerous: the first startup may partially apply the file and fail later; the next startup then fails immediately on a duplicate earlier column.

Preferred order:

1. Add a real migration-history table and apply each numbered migration once.
2. If the app intentionally uses idempotent startup reconciliation, add columns through `PRAGMA table_info`/`columnExists` checks in Go, then run only idempotent `CREATE TABLE/INDEX IF NOT EXISTS` SQL.
3. If supporting a legacy partially-applied additive migration, execute statements individually and tolerate only SQLite's exact duplicate-column error; never suppress unrelated SQL failures.

Add a test that runs migration twice and a test that starts from each plausible partially-applied state. Deployment is incomplete until the service restarts successfully against the existing live database.

## Verification

- New Board returns zero Columns.
- Create/archive Column works and foreign Project IDs fail.
- Two todo Jobs append in stable order; reorder persists after reload.
- Reordering a non-todo or foreign Job fails without partial updates.
- Job Dialog shows all messages and posting refreshes the same conversation.
- Provider secret is absent from all GET/PATCH responses; blank update preserves it.
- Project Default workspace persists on create and edit.
- Run backend tests/build and frontend tests/build.
- Deploy frontend and backend, restart the real service, poll readiness, then verify local and public health plus deployed bundle markers.
- Commit only after restart and public verification; push only when a configured remote exists, otherwise report the committed-but-unpushed state honestly.
