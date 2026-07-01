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
When publishing photos/videos to Facebook, the `url` parameter must point to a publicly accessible URL. Internal file paths won't work. Prepend the server's public base URL to relative media paths before passing them to the Facebook API.
