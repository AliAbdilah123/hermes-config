# Migration-order table rebuild schema loss

Use when a SQLite API starts returning generic internal errors after independently developed migrations touched the same table.

## Failure pattern

A later migration rebuilds a table with `RENAME → CREATE → INSERT → DROP`. An earlier migration added a column to the old table. If the rebuild's `CREATE TABLE` omits that column, the migration ledger can show both migrations as applied while the live schema has silently lost it. Current queries then fail with `no such column`.

This is especially easy to miss when migrations share a numeric prefix: filename lexical order—not feature chronology—controls execution.

## Diagnosis

1. Read the failing query and list its expected columns.
2. Inspect `PRAGMA table_info(<table>)` on the effective runtime database.
3. Compare live columns with the migration ledger and every migration that creates or rebuilds the table.
4. If an add-column migration is recorded but its column is absent, find a later table rebuild that omitted it.
5. Run `PRAGMA integrity_check` to distinguish schema drift from corruption.

## Repair

- Preserve existing data.
- Add an idempotent repair that checks `PRAGMA table_info` and adds the missing nullable column only when absent.
- Correct the rebuild migration for fresh databases so its final table includes all previously introduced columns.
- Never delete a ledger row merely to force replay; non-idempotent migration replay can fail or damage data.
- If migrations have not shipped, renumber or fold them into one coherent sequence. If shipped, append a uniquely numbered repair migration.

## Regression matrix

1. **Fresh bootstrap:** all migrations produce the final schema.
2. **Historical upgrade:** simulate both migrations recorded but the rebuilt table missing the column; migrating restores it without losing existing rows.
3. Exercise the exact query that failed, not only database open/migration success.

## Deployment gate

Back up the effective runtime database, run integrity check, deploy the exact binary, restart, verify local health, then exercise the authenticated endpoint selecting the repaired column. Process health alone is insufficient.
