# SQLite table-rebuild migration drift

Use when a deployed SQLite application starts returning generic API errors after a restart or migration, especially when multiple migrations share a numeric prefix or one migration rebuilds a table.

## Failure pattern

SQLite schema migrations often emulate constraint changes by:

1. renaming the original table;
2. creating a replacement table;
3. copying rows;
4. dropping the original table.

If an earlier migration added columns and a later rebuild uses an outdated `CREATE TABLE` definition, the rebuild silently removes those columns. The migration ledger can still show both migrations as applied, so restarting does not repair the schema. Application queries selecting the lost column then fail with a generic internal error.

Same-number filenames such as `0006_feature_a.sql` and `0006_feature_b.sql` make ordering assumptions especially fragile: lexical ordering, deployment timing, and historical databases can produce different final schemas.

## Diagnosis

1. Identify the runtime database from the effective service configuration, not by filename proximity.
2. Run `PRAGMA integrity_check`; corruption and schema drift are separate problems.
3. Compare `PRAGMA table_info(<table>)` with every column selected or written by current code.
4. Inspect `schema_migrations` and the complete migration scripts in execution order.
5. Look specifically for `ALTER TABLE ... RENAME`, replacement `CREATE TABLE`, and copy statements that omit newer columns.
6. Reproduce the failing query against the runtime schema or a safe backup. A healthy service and database integrity check do not prove query/schema compatibility.

## Durable repair

- Back up the live database using SQLite backup APIs or `.backup`; verify the backup with `PRAGMA integrity_check` before deployment.
- Repair the migration chain for clean databases so the replacement table contains the complete current schema.
- For already-affected databases, add an idempotent post-migration schema invariant or a uniquely named corrective migration that checks whether the column exists before adding it.
- Do not merely delete or edit the migration-ledger row on production: replaying a table rebuild can duplicate work or destroy data.
- Avoid unconstrained dynamic SQL in a generic `ensureColumn` helper. If identifiers are constants, keep the helper private and call it only with compile-time table/column definitions; otherwise whitelist identifiers.

## Regression matrix

Verify both histories:

1. **Clean bootstrap:** empty database applies all migrations and exposes the complete schema.
2. **Historical upgrade:** construct the pre-fix schema with all ledger rows marked as applied but the rebuilt table missing the column; opening/migrating repairs it idempotently.
3. Reopen the repaired database a second time to prove no duplicate-column failure.
4. Run the exact list/detail query that previously failed.
5. Confirm preserved row counts and representative data before and after repair.

## Deployment proof

1. Build and install the exact binary named by systemd `ExecStart`.
2. Restart and wait for local health readiness.
3. Re-check the live table schema and database integrity.
4. Exercise the exact authenticated public API route that failed; unauthenticated `401`, health `200`, or frontend HTML `200` is insufficient.
5. Clean any dedicated E2E identity and confirm zero fixture rows remain.
6. If the fix includes frontend behavior, build with the deployment base path and publish to the nginx document root separately.
