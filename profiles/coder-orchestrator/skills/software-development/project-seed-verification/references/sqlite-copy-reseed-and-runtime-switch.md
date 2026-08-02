# Safe SQLite copy → reseed → runtime switch

Use when production-like fixture data must replace the active SQLite dataset without risking the original.

## Invariants

- Never reseed the active database in place.
- Treat the main DB plus `-wal` and `-shm` sidecars as one live database state.
- Preserve both a SQLite-consistent backup and the stopped-runtime file set.
- Do not change schema while regenerating data.

## Procedure

1. **Identify the actual runtime file** from the running process/service environment and working directory. Check every path selector the application supports; do not infer it from filenames nearby.
2. **Inspect journal mode and sidecars.** A large `DB-wal` means a filesystem copy of only `DB` can omit committed data.
3. **Create the immutable backup through SQLite's backup API** while the service is live:

```python
import sqlite3
with sqlite3.connect("file:sqlite.db?mode=ro", uri=True) as src:
    with sqlite3.connect("sqlite.db.original.bak") as dst:
        src.backup(dst)
```

4. Verify the backup with `PRAGMA integrity_check`, record its SHA-256, then make a second SQLite-backup-derived working copy. Make the immutable backup read-only.
5. **Regenerate only the working copy.** Keep schema objects untouched. Prefer transactional `DELETE`/`INSERT` data replacement with foreign keys disabled only for ordered bulk replacement; re-enable afterward.
6. Validate before promotion:
   - compare normalized `sqlite_master` rows between original and candidate;
   - `PRAGMA integrity_check` returns `ok`;
   - `PRAGMA foreign_key_check` returns no rows;
   - assert required roles, realistic relationships, non-null completeness, enum/check-compatible values, prices/quantities, sessions, packages/entries, and auth password hashes;
   - run focused application checks. Keep unrelated broad-suite failures separate and identify exact failing tests.
7. **Switch with the service stopped.** Move—not delete—the old `DB`, `DB-wal`, and `DB-shm` together into a timestamped archive directory. Move the verified candidate into the configured active path, preserve ownership/mode, restart, and confirm the new process resolves every DB selector to that path.
8. Re-run integrity and foreign-key checks against the live file after restart.
9. Perform authenticated public E2E through the real HTTPS route for every required role. Verify positive permissions and negative authorization (for example, a basic user receives `403` on admin routes), plus representative localized data and complete package/session/member flows.

## Reporting boundaries

Report the public URL, immutable backup path and checksum, stopped-runtime archive path, role credentials, focused verification, and any unrelated suite failures separately. A database-only operation does not require a source commit; never manufacture one, and never absorb unrelated dirty-tree changes.

## Pitfalls

- `cp sqlite.db backup.db` while WAL is active is not a safe committed-state backup.
- Renaming only the main DB while leaving old sidecars at the active path can corrupt or contaminate the replacement.
- `PRAGMA foreign_keys` may be disabled on a read connection; use `foreign_key_check` as the data-integrity gate.
- A successful login alone does not verify role wiring. Probe each role's allowed route and at least one forbidden route.
- Public API JSON collection shapes may be either a bare list or `{ "data": [...] }`; normalize the shape in verification rather than weakening assertions.
