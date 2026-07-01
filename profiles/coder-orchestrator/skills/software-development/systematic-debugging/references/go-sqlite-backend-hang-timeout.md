# SQLite-Backed Go Backend Hang / Timeout

## Symptom

POST/PUT requests to a SQLite-backed Go backend hang indefinitely (or timeout after the client deadline, e.g. 15 s), while GET-only endpoints (health, no-body handlers) respond normally. The backend process appears healthy (`systemctl status` shows `active (running)`).

The client message is usually generic: `"Request timed out. Check your connection and try again."`

## Root Cause Pattern

This specific pattern — POST bodies hang but GET works — indicates a request-handling goroutine is stuck waiting on a resource held by another goroutine. In SQLite-backed apps with `SetMaxOpenConns(1)`, the most common cause is a **blocked background publisher goroutine** that acquires a database connection and then performs blocking HTTP calls (Meta Graph API, Instagram publishing) without releasing the connection.

The chain:

1.  `db.SetMaxOpenConns(1)` — single SQLite connection pool.
2.  Background goroutine (`runPublishCycle`) runs on startup and periodically.
3.  If it acquires the connection and proceeds to call external HTTP APIs (Facebook/Instagram) with a 15 s+ timeout, ALL other requests that need the database connection will block.
4.  GET `/health` works because it never touches the database.
5.  GET `/api/auth/get-session` may work if the background goroutine hasn't acquired the lock yet.
6.  POST `/api/auth/sign-in/email` or any POST with body that hits a DB-using handler hangs.

## Investigation

1.  **Health first:** `curl http://127.0.0.1:8089/health`. If it returns quickly, the HTTP server is alive and the listener is accepting.
2.  **Narrow the request:**
    *   Test a GET endpoint that uses the database (`get-session`, `dashboard`). If fast → DB pool not completely dead.
    *   Test a POST endpoint without a body (`analytics/refresh`). If fast → POST method itself is fine.
    *   Test a POST with a body that touches the database (`signin`, `signup`). If this hangs → the suspect is a goroutine holding the DB connection.
3.  **Check the database lock:** Read the background publisher code (`internal/posts/publisher.go`). Look for `app.DB.Query` calls followed by HTTP client calls in the same goroutine.
4.  **Reproduce:** The pattern `GET works, POST hangs` is a strong signal that the DB pool is blocked.

## Fix

1.  **Immediate:** `sudo systemctl restart <service>.service`. This breaks the lock and restores all requests immediately.
2.  **Permanent fixes (apply one or more):**
    *   Ensure the publisher goroutine **releases the database connection before making HTTP calls** — read rows into memory, close the result set, then iterate.
    *   Increase `SetMaxOpenConns` to at least 5 and add WAL mode + busy timeout. Preferred single-patch fix:

        ```go
        db.SetMaxOpenConns(5)
        db.SetMaxIdleConns(5)
        _, _ = db.Exec(`PRAGMA busy_timeout=5000; PRAGMA journal_mode=WAL;`)
        ```

        This allows concurrent readers/writers (WAL) so the publisher's HTTP calls don't starve auth and dashboard requests, and the busy timeout prevents lock errors on contention.
    *   Add a stricter timeout to the publisher goroutine's HTTP client (e.g. 10 s) so it cannot block indefinitely.
    *   Move the publisher to a separate SQLite connection (open a second `*sql.DB` for the publisher only).

## Verification

After the restart (or fix), verify both locally and publicly:

```bash
# Local: single request
curl -s --max-time 5 -X POST http://127.0.0.1:8089/api/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test12345"}'
```

Expect a fast (sub-second) response with either `401 INVALID_EMAIL_OR_PASSWORD` (for bad credentials) or `200` (for valid credentials). No timeout.

**Loop verification** — confirms the fix survives publisher tick cycles:

```bash
jar=$(mktemp)
for i in 1 2 3; do
  curl -s --max-time 8 -c $jar -b $jar \
    -X POST http://127.0.0.1:8089/api/auth/sign-in/email \
    -H 'Content-Type: application/json' \
    -d '{"email":"demo@example.local","password":"password123"}' \
    -w "login$i HTTP %{http_code} time=%{time_total}\n" -o /dev/null
  curl -s --max-time 8 -c $jar -b $jar \
    http://127.0.0.1:8089/api/dashboard \
    -w "dash$i HTTP %{http_code} time=%{time_total}\n" -o /dev/null
  sleep 25  # spans at least one publisher tick
done
rm $jar
```

All iterations should return 200 in under 1 second. If any iteration times out, the fix didn't take.
