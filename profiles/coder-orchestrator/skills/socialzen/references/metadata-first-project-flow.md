# Metadata-first Project creation in a shared composer architecture

Use this when a Project record must exist before destinations or publishable content are selected.

## Minimal architecture

- Keep the existing Project aggregate; do not add a mirror table.
- Add a metadata-only create boundary accepting only title and optional description.
- Persist a DRAFT without targets, media, quota reservation, immutable version, publication run, queue work, or publishing analytics.
- Route the returned ID into the existing composer.
- In composer existing-record mode, patch Draft metadata/content and invoke the existing per-Project publish endpoint after Review. Never POST a second Project.
- Treat description as internal Project metadata, not social caption.

## SQLite nullability migration

If the aggregate has a required destination/account foreign key, metadata-first creation may require making it nullable. SQLite needs a guarded table rebuild:

1. Detect current `PRAGMA table_info` nullability and no-op when already migrated.
2. Disable foreign keys on one dedicated connection before beginning the transaction.
3. Create the replacement table with the complete current row shape.
4. Copy all rows, drop the old table, rename the replacement, and commit.
5. Re-enable foreign keys and run `PRAGMA foreign_key_check`.
6. Test preservation of dependent targets, media, versions, publication runs, attempts, metrics, and quota rows.

Production databases can contain pre-existing foreign-key violations unrelated to the rebuild. A migration must not enter a restart loop merely because the global post-migration check discovers old damage. Establish the pre-migration baseline and fail only on newly introduced violations, or repair/explicitly account for baseline violations before deployment. Always inspect the first restart logs and wait for stable service readiness; `systemctl is-active` immediately after restart can briefly report active before migration failure and automatic restart.

## Delivery verification

- Focused backend tests: metadata validation, ownership, zero publishing side effects, list/detail shape, legacy title fallback, graph-preserving migration.
- Focused frontend tests: every New Project entry route, accessible creation form, same-ID composer endpoint selection, metadata cards.
- Build and typecheck.
- Deploy backend and exact lazy route chunks.
- Probe health after a stable readiness interval and inspect restart logs for migration failures.
- Verify public HTML references the new entry bundle and probe the creation-page, composer, and library lazy chunks for stable markers.
- An unauthenticated 401 proves the public API boundary is wired, not the authenticated create→compose→review→publish workflow. Do not call this exact public E2E without a real signed-in browser session.
