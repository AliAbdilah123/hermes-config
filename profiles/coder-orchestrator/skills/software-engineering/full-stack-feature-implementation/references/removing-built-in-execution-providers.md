# Removing Built-in Execution Providers Cleanly

Use when deleting built-in agent/delegate providers (for example Codex or Claude Code) from a Go + SQLite + Vite job application while retaining another execution path or user-defined tools.

## Scope map

Search and classify every provider coupling before editing:

- Settings UI selector and frontend settings types/payloads
- Settings API validation, serialization, and persistence
- User-level default-provider column
- Job-level snapshotted provider column and API DTO
- Scheduler dispatch branches and provider-specific command construction
- Provider adapter/config fields and tests
- Built-in tool discovery/list entries
- Generated or embedded frontend assets
- README/config examples

Do not stop after deleting provider labels or adapters. A selector column that can now hold only one value is obsolete state, not compatibility.

## SQLite migration

SQLite column removal should be an idempotent table rebuild when compatibility or SQLite version makes `DROP COLUMN` unsuitable:

1. Detect obsolete columns with `pragma_table_info`.
2. Start a transaction.
3. Create replacement tables with the final schema and all unrelated constraints/index semantics.
4. Copy only retained columns.
5. Drop old tables and rename replacements.
6. Recreate affected indexes/triggers if any.
7. Preserve foreign-key relationships and unrelated rows.
8. Rebuild custom-tool tables only if they also contain obsolete provider command fields; preserve their `argv_json` or equivalent execution definition.
9. Commit and prove a second startup/migration is a no-op.

Add a migration regression that constructs the legacy schema, inserts unrelated/custom-tool data, runs migration, then asserts:

- obsolete settings/job columns are absent;
- unrelated rows remain;
- custom tool definitions remain intact;
- fresh-schema startup and repeated migration both succeed.

## Execution model decision

Distinguish built-in providers from genuinely independent execution paths. Removing Codex/Claude does not automatically require deleting Hermes API or custom CLI tools. However, do not retain `default_provider`/`cli_tool` columns merely to represent a single remaining built-in provider. If custom tools remain selectable per job, model that explicitly; otherwise remove the dead selection state and use the sole execution path directly.

## Verification

- Search source (excluding generated assets where appropriate) for removed provider names and obsolete field names.
- Run backend tests and build.
- Run frontend tests and production build.
- Rebuild embedded frontend assets before the backend binary.
- Restart and wait for HTTP readiness; inspect service logs if readiness fails.
- Verify the public HTML references the new asset hash and the deployed production JS lacks removed UI/settings markers.
- Commit after deployment verification; push when a remote exists, and report explicitly when none is configured.
