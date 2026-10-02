# SQLite social-event foreign-key repair

Use when a signed Instagram/Facebook webhook reaches the expected processor and matches an active integration, but repeatedly ends as `processing_failed` and no note persists.

## Diagnostic pattern

1. Correlate the exact privacy-safe sender, recipient, and message hashes in the service journal.
2. Confirm processing actually ran and identify the last successful boundary (for example, active integration matched).
3. Inspect both the current parent table and receipt/event table schemas:
   ```sql
   .schema notes
   .schema instagram_note_events
   PRAGMA foreign_key_list(instagram_note_events);
   PRAGMA foreign_key_check;
   ```
4. Watch for a child FK that followed a renamed table during an older SQLite rebuild, e.g. `REFERENCES notes_before_facebook(id)` after that temporary table was dropped. The note insert and event insert share one transaction, so the late event failure rolls back the apparently successful note insert.

## Minimal repair

Add a forward migration that rebuilds only the child event table:

```sql
CREATE TABLE instagram_note_events_repaired (
  external_message_id TEXT PRIMARY KEY,
  note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE
);
INSERT INTO instagram_note_events_repaired SELECT external_message_id, note_id FROM instagram_note_events;
DROP TABLE instagram_note_events;
ALTER TABLE instagram_note_events_repaired RENAME TO instagram_note_events;
```

Do not patch around the FK in application code or disable foreign keys.

## Regression and deployment

- RED: construct the historical pre-repair schema, retain one event row, run migrations, and assert the FK target is `notes` plus the row is preserved.
- Ensure the fixture removes the repair migration from the migration ledger; corrupting a fully migrated DB without doing that falsely tests migration idempotence rather than upgrade behavior.
- Add privacy-safe logging of the returned processing error; never log message content or tokens.
- Back up the live SQLite DB using `.backup`, then integrity-check the backup.
- Build and install the exact binary named by systemd, restart, and verify health.
- Require: migration ledger entry present, FK target corrected, `PRAGMA integrity_check` clean, and no unexpected `foreign_key_check` violations.
- Let provider retries prove the live path when available: require the same hashed message to move from `processing_failed` to `result=ok`, `processed=1`, and exactly one persisted event/note. Do not manually forge a signed provider webhook.
- Commit only migration, focused regression, and coherent logging changes; keep runtime DB backups untracked.
