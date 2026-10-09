# Safe Account Provisioning and Password Reset (Go + SQLite)

Use this runbook for administrative account creation, role assignment, and password resets in the deployed SocialZen application.

## Procedure

1. Identify the exact deployed service, working directory, environment file, listener, and database path from the systemd unit and runtime configuration. Do not assume a similarly named repository or database is live.
2. Inspect the live `users` schema and the application's current password implementation before mutation. Hash formats can change; source code is authoritative.
3. Confirm the normalized-email match count before changing anything:
   ```sql
   SELECT id, email, role, account_state, email_verified
   FROM users WHERE lower(email)=lower(?);
   ```
   - Reset/update: require exactly one match.
   - Create: require zero matches; if one exists, update it only when that is the requested outcome.
4. Generate hashes with the application's own algorithm and parameters. SocialZen currently uses `pbkdf2-sha256$120000$<base64url-salt>$<base64url-key>` with a random 16-byte salt and 32-byte SHA-256 key. Re-check `passwords.go` rather than treating these parameters as permanent.
5. Back up the live SQLite database immediately before mutation and preserve its ownership/mode.
6. Use `BEGIN IMMEDIATE`; require each update row count to equal one and roll back on mismatch. For creation, populate all required lifecycle fields and assign the exact requested role (`USER` or `SUPERADMIN`), active state, verification state, timezone, terms metadata, and timestamps according to the live schema.
7. Read the hash back and independently verify the supplied password using PBKDF2 parsing and constant-time comparison. Never print plaintext passwords or full hashes.
8. Exercise the real sign-in endpoint for every account twice:
   - directly against the localhost application listener;
   - through the public domain/reverse proxy.
   Require successful statuses from both, then query only non-secret fields to verify role/state.
9. Delete temporary request/response and hash-helper files. A database-only mutation normally needs no restart because authentication reads SQLite per request.

## SQLite and Shell Pitfalls

- SQLite `RAISE()` is only valid inside trigger programs. Use application code such as Python stdlib `sqlite3` to transact, inspect `cursor.rowcount`, and commit only when valid.
- Avoid putting passwords in command-line arguments, shell history, logs, or final reports beyond what the user already supplied. Prefer a mode-0600 temporary helper or stdin and remove it immediately.
- Login verification should discard response bodies and must never expose cookies or session tokens.

## Completion Standard

Do not report success until the backup exists, hashes verify independently, roles/states match, and both localhost and public login probes succeed for every requested account.
