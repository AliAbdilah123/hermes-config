# Safe Account Password Reset (Go + SQLite + bcrypt)

Use this runbook for administrative password resets in deployed Go applications that store bcrypt hashes in SQLite.

## Procedure

1. Identify the exact deployed service, working directory, environment file, and database path from the systemd unit and runtime configuration. Do not assume a similarly named repository or database is live.
2. Confirm exactly one account matches the normalized email before changing anything:
   ```sql
   SELECT id, email, length(password_hash), substr(password_hash,1,4)
   FROM users WHERE lower(email)=lower(?);
   ```
3. Generate the replacement hash with the application's own password library and cost. For this codebase, use `golang.org/x/crypto/bcrypt.GenerateFromPassword(..., bcrypt.DefaultCost)`; never store plaintext or invent a different hash format.
4. Back up the live SQLite database immediately before mutation.
5. Use a transaction and require the update row count to equal one. Roll back otherwise. Update `updated_at` if the schema expects it.
6. Verify the stored hash independently with `bcrypt.CompareHashAndPassword`.
7. Exercise the real login endpoint twice:
   - directly against the localhost application listener;
   - through the public domain/reverse proxy.
   Require the expected successful status from both. Delete temporary request/response and hash-helper files afterward.
8. A password-hash change normally needs no service restart because authentication reads the database per request.

## SQLite CLI Pitfall

The machine's sqlite3 configuration may print column headers even in command substitution. Use `sqlite3 -noheader ...` when extracting a hash; otherwise verification can fail because the captured value begins with the column name rather than `$2a$`/`$2b$`.

SQLite `RAISE()` is only valid inside trigger programs. For an exact-one-row administrative update, use application code (for example Python stdlib `sqlite3`) to begin an immediate transaction, inspect `cursor.rowcount`, and commit only when it equals one.

## Security

- Do not print plaintext passwords or full password hashes in logs.
- Restrict backups and database files to their existing owner/mode.
- Do not report success until bcrypt verification and both login probes pass.
- Never include cookies, session tokens, or response bodies in the final report.
