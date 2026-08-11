# SQLite Single-Connection Self-Deadlock Behind Nginx 504

## Trigger

Use this diagnosis when a SQLite-backed upstream shows this split:

- Static pages and `/health` remain fast.
- Unauthenticated requests remain fast because middleware rejects them before touching SQLite.
- Authenticated or DB-backed endpoints hang together and become nginx/Cloudflare `504`s.
- Restarting restores service only until a particular endpoint runs.
- The process stays alive and `PRAGMA integrity_check` passes.

## Root-cause pattern

With `db.SetMaxOpenConns(1)`, active `*sql.Rows` owns the only connection. A nested `db.Exec`, `db.Query`, or `db.QueryRow` before those rows are drained and closed waits forever for another connection:

```go
rows, err := db.Query(`SELECT id FROM due_items`)
if err != nil { return err }
defer rows.Close()
for rows.Next() {
    var id int64
    if err := rows.Scan(&id); err != nil { return err }
    _, err = db.Exec(`INSERT OR IGNORE INTO notifications(item_id) VALUES(?)`, id) // deadlock
}
```

The deferred close is too late: the function cannot return because `Exec` waits for the connection held by `rows`.

## Evidence recipe

1. Correlate the first hanging endpoint with nginx upstream timeout timestamps. A failure cluster exactly one proxy timeout later suggests one request captured a shared resource and others queued.
2. Compare health, unauthenticated, and authenticated DB-backed probes.
3. Inspect `SetMaxOpenConns` and loops over `rows.Next()` for nested DB operations.
4. Inspect qualifying production data read-only. A due source row plus no generated target row proves execution enters the blocking branch.
5. Check restart chronology for temporary recovery followed by failure after the trigger endpoint.
6. Check SQLite integrity to separate pool starvation from corruption.

## Minimum fix

Materialize candidates, check `rows.Err()`, explicitly close rows, then write. An atomic `INSERT OR IGNORE ... SELECT ...` is also valid when the transformation fits SQL.

Do **not** increase `MaxOpenConns` as the primary fix; it masks the ownership bug and can introduce SQLite write contention or inconsistent connection-local pragmas. As hardening, use request-scoped `QueryContext`/`ExecContext` so cancelled requests stop waiting.

## Regression test

With `SetMaxOpenConns(1)` and a short deadline:

1. Seed one qualifying due item.
2. Invoke the trigger endpoint and require success before the deadline.
3. Assert one target row was inserted.
4. Repeat and assert idempotency.
5. Concurrently invoke another DB-backed endpoint and require completion.
6. Assert `db.Stats().InUse == 0` afterward.

A broad suite that never seeds a qualifying row will miss this deadlock even when every existing test passes.