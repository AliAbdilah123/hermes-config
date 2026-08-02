# SQLite copy-first reseed and runtime promotion

Use when replacing Komuna's demo/test dataset while preserving the current database and schema.

## Safety invariant

Never reseed, truncate, delete, rename, or overwrite the active SQLite file first. The sequence is always:

1. Discover the database actually opened by the running process from `/proc/<pid>/environ` or the service definition; do not infer it from nearby filenames.
2. Record the process working directory, DB path, file owner/mode, and initial `PRAGMA integrity_check`.
3. Create a consistent immutable backup with Python `sqlite3.Connection.backup()`, SQLite `.backup`, or `VACUUM INTO`. A filesystem `cp` is unsafe while WAL-backed writes may be active.
4. Create a separate working copy from that backup. Make the archival backup read-only and record its absolute path plus SHA-256.
5. Regenerate data only in the working copy. Do not recreate tables, apply schema migrations, or run destructive code against the active DB.
6. Compare complete `sqlite_master` definitions between original backup and working copy. Require exact equality for tables, indexes, triggers, and views.
7. Validate the working copy before promotion:
   - `PRAGMA integrity_check = ok`
   - `PRAGMA foreign_key_check` returns zero rows
   - required role/auth identities can sign in
   - every program has products, packages, package entries, future/past sessions, managers, and representative transactional state
   - numeric/text values match the existing SQLite affinity and application contract
8. Stop or quiesce the API, create one final consistent snapshot if writes may have occurred since step 3, then atomically promote the validated file at the exact configured DB path. Preserve the pre-promotion file under a timestamped immutable name; never remove it.
9. Restore owner/mode, restart, and verify the process reopened the promoted inode/path.
10. Run authenticated public E2E for superadmin, program admin, manager, member, and a basic user with no membership. Verify role-specific navigation and at least one representative program flow.

## Seed quality for Indonesian/Kalimantan Timur fixtures

- Use Indonesian names, UI-facing text, prices in IDR, `Asia/Makassar`, and explicit `Kalimantan Timur` locations.
- Give every program complete, internally connected records—not just catalog rows. Include admins, managers, members, session and Simple products, package entries, schedules, assignments, purchases, vouchers/subscriptions, claims, notifications, and audit history where supported.
- Keep a basic authenticated user outside all programs to test discovery/join flows.
- Keep superadmin platform-scoped unless a scenario explicitly needs program membership.
- Use the application's own password hash algorithm and verify all dedicated test credentials before promotion.

## Operational pitfalls

- A rich PostgreSQL/Neon TypeScript seed is not automatically valid for the deployed Go/SQLite API; inspect the active schema and runtime first.
- `PRAGMA foreign_keys` may be disabled on a connection. This does not excuse orphaned fixtures: always run `PRAGMA foreign_key_check` after generation.
- Do not claim schema preservation from table names alone; compare normalized `sqlite_master` rows.
- Do not commit unrelated source changes merely because the shared checkout is dirty. A data-only reseed can remain a runtime artifact, while commits should contain only deliberate reusable seed tooling if requested.
- Do not call the task complete after local integrity checks. Promotion and authenticated public E2E are separate gates.
