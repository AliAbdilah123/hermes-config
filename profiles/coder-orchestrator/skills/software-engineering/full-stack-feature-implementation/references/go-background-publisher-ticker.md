# Go Background Publisher with time.NewTicker

Use this when adding a background cron-like task to a Go HTTP server — polling, scheduled publishing, cleanup jobs, or any periodic work that must run alongside `http.ListenAndServe`.

## Pattern

```go
func main() {
    // ... setup app, DB, models ...

    // Background publisher: run every N minutes
    go func() {
        ticker := time.NewTicker(5 * time.Minute)
        defer ticker.Stop()
        // Optionally: run once immediately on startup
        runCycle(appModel)
        for range ticker.C {
            runCycle(appModel)
        }
    }()

    log.Fatal(http.ListenAndServe(addr, routes()))
}
```

Key decisions:
- **`go func()` goroutine**: runs alongside the HTTP server. Both exit when the process exits.
- **`time.NewTicker`**: fires at fixed intervals, not drifting. Simpler than `time.AfterFunc` chains.
- **Deferred `ticker.Stop()`**: ensures cleanup (though unreachable after `ListenAndServe`).
- **Initial run**: optional — useful when the server just restarted and there may be backlog.

## Typical cycle function

```go
func runCycle(m *models.App) {
    now := time.Now().UTC().Format(time.RFC3339)

    // Phase 1: enqueue — transition pending items to in-progress
    m.DB.Exec(
        `UPDATE posts SET status='PUBLISHING', updated_at=?
         WHERE status='SCHEDULED' AND publish_at<=?`,
        now, now,
    )

    // Phase 2: process — do the actual work for each in-progress item
    processed, ok, failed := processDueItems(m)
    if processed > 0 {
        log.Printf("cycle: %d processed, %d succeeded, %d failed", processed, ok, failed)
    }
}
```

## Pitfalls

### Don't use SELECT in a loop without batching
Always `LIMIT N` in polling queries to avoid OOM on large backlogs. Unprocessed items get picked up on the next tick.

### Partial success must be handled
If a post has multiple targets (Facebook + Instagram) and one succeeds while the other fails:
- Mark the successful target as `PUBLISHED`
- Mark the failed target as `FAILED` with an `error_message`
- Leave the parent post as `PUBLISHING` for retry on the next tick
- Only mark parent as `PUBLISHED` when ALL targets succeed
- Only mark parent as `FAILED` when ALL targets failed

### Don't expose the publish trigger as a public endpoint
The background ticker handles the work. If you add a manual trigger route for debugging, restrict it (auth gate + localhost-only) or delete it before deploying. An unauthenticated public POST endpoint that triggers publishing is a DoS vector.

### Billing/quota must only count real publishes
Count only `PUBLISHED` posts, not `PUBLISHING` or `SCHEDULED`. Remove any "auto-publish" hacks that mark posts published without API calls (e.g., a GET handler that silently transitions `SCHEDULED → PUBLISHED` when `publish_at` has passed).

### Test with a no-op case
Always verify the cycle handles an empty DB gracefully:

```go
func TestCycleNoOp(t *testing.T) {
    db := openTestDB(t)
    app := &models.App{DB: db}
    processed, ok, failed := runCycle(app)
    if processed != 0 || ok != 0 || failed != 0 {
        t.Fatalf("empty DB: got processed=%d ok=%d failed=%d, want all zero", processed, ok, failed)
    }
}
```

### Facebook Graph API: use page_id, not internal DB id
The `facebook_pages` table has both `id` (internal PK) and `page_id` (Facebook's numeric page ID). Publishing must use `page_id` in the Graph API URL (`/{page-id}/feed`), not the internal DB `id`. Always `SELECT page_id, access_token_encrypted` together.

### Media URLs must be publicly accessible
When publishing photos/videos to Facebook/Instagram, the `url` parameter must point to a publicly accessible URL. Internal file paths won't work. Prepend the server's public base URL to relative media paths before passing them to the Graph API.

**Critical sub-pitfall — nginx domain config and DB-stored media URLs**: When a project migrates from path-based deployment (`/projects/<slug>/`) to a custom domain, the media URLs stored in the database (e.g. from `SaveUpload` returning `/projects/<slug>/media/user_.../upload_...jpg`) still use the full path prefix. If the domain's nginx server block only has `location ^~ /media/` but NOT `location ^~ /projects/<slug>/media/`, those media URLs fall through to the SPA catch-all and return HTML instead of the image. External platforms (Instagram/Facebook) silently receive HTML, causing publish failures with no visible error. Always proxy BOTH path variants in the domain config, and set `PUBLIC_BASE_URL` in `.env` so the Go publisher constructs full URLs.

### SQLite cursor-write conflict (modernc.org/sqlite) — SILENT failures
With `modernc.org/sqlite` (pure-Go driver, no cgo), the connection pool can have multiple connections. If you keep a `Rows` cursor open (`defer rows.Close()`) and then call `DB.Exec` for writes inside the same loop, the writes can silently fail — no error returned, but the UPDATE doesn't take effect. This manifests as posts published to the platform API but their DB target status never updating from `PUBLISHING` to `PUBLISHED`.

**Root cause**: SQLite only allows one writer at a time. With multiple connections in the pool, a read cursor on one connection can block a write on another. The `Exec` call may return nil error but the write doesn't land.

**Fix pattern — read all rows into memory, close cursor, THEN write:**

```go
// BAD: cursor open during writes (silent UPDATE failures)
rows, _ := db.Query("SELECT ...")
defer rows.Close()  // stays open during all writes below!
for rows.Next() {
    // ... read ...
    db.Exec("UPDATE ...")  // can silently fail
}

// GOOD: read into slice, close cursor, then write
rows, _ := db.Query("SELECT ...")
items := make([]item, 0)
for rows.Next() {
    var it item
    rows.Scan(&it.id, ...)
    items = append(items, it)
}
rows.Close()  // cursor closed BEFORE any writes

for _, it := range items {
    db.Exec("UPDATE ...")  // safe — no open cursors
}
```

**Also**: call `db.SetMaxOpenConns(1)` after opening the SQLite database to prevent concurrent access entirely. This serializes all queries through one connection, eliminating lock contention.

### Orphaned PUBLISHING targets
When a parent post transitions out of `PUBLISHING` (e.g. to `PUBLISHED` or `FAILED`), its `post_targets` rows can remain stuck at `PUBLISHING` if the write failed (see SQLite pitfall above). Add a cleanup step at the top of each cycle:

```go
m.DB.Exec(
    `UPDATE post_targets SET status='FAILED', error_message='Parent post no longer publishing', updated_at=?
     WHERE status='PUBLISHING' AND post_id NOT IN (SELECT id FROM posts WHERE status='PUBLISHING')`,
    now,
)
```

### Add error logging for each target
When a target publish fails, log the post ID, target ID, platform, and error message. Without per-target logging, the only signal is the parent post's generic `"All platforms failed to publish"` — which tells you nothing about whether the issue was Instagram auth, media URL accessibility, or a Graph API error.

```go
log.Printf("publisher: post %s target %s (%s) failed: %s", post.id, t.id, t.platform, result.Error)
```