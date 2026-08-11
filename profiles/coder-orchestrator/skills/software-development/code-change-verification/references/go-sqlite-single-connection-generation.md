# Go SQLite single-connection generation verification

Use for Go endpoints that query candidates and then materialize notifications, reminders, queue items, or summaries in SQLite.

## Deadlock pattern

With `db.SetMaxOpenConns(1)`, an open `*sql.Rows` owns the only connection. Calling `db.Exec`, another query, or `db.Begin` before those rows close waits forever for a second connection. The triggering endpoint hangs and other DB-backed authenticated requests queue behind it. Raising the connection limit can hide the lifecycle defect.

## Minimal implementation shape

1. Query candidates.
2. Scan all candidates into a small in-memory slice.
3. Treat scan errors as fatal.
4. Capture `rows.Err()`.
5. Close rows explicitly and check the close error.
6. Only after successful close, perform inserts or updates.
7. Preserve the intentional one-connection limit.

A deferred `rows.Close()` is insufficient when writes happen later in the same function: the defer runs after those writes attempt to acquire a connection.

## Regression contract

Use a real SQLite handle configured with exactly one open connection. Seed one eligible candidate and invoke the real authenticated HTTP route with a bounded timeout. Prove:

- generation completes;
- the expected row is created;
- a second call remains idempotent (exactly one row);
- `db.Stats().InUse == 0` after the response;
- another authenticated DB-backed request completes immediately afterward.

The timeout detects the original hang; the row-count assertion proves generation rather than mere response completion.

## Public deployment proof

1. Rebuild the exact binary named by systemd and restart it.
2. Poll local readiness, then use the public hostname.
3. Create an isolated authenticated account and satisfy ordinary product gates such as onboarding. Inspect a `403` response body before blaming a CDN/WAF; JSON like `onboarding_required` is application authorization.
4. If direct fixture setup is unavoidable, inspect the live schema and write as the service/database owner (for example `sudo -u www-data sqlite3 ...`) so OS permissions do not create a false read-only failure.
5. Seed one eligible candidate, call the public generation endpoint twice, and verify prompt `200` responses, visible candidate data, and one persisted row.
6. Call a second authenticated endpoint and verify it returns promptly.
7. Remove only the isolated fixture records.

Do not modify a real user’s records or require their credentials merely to prove the repair.