# Posts list deadlock when published posts appear to disappear

## Symptom

After restarting `socialzen.service`, the Posts page/API can appear to show only failed/error posts or hang while published posts seem to disappear. `/health` stays fast because it does not touch SQLite.

## Root cause

Production intentionally uses `db.SetMaxOpenConns(1)` with `modernc.org/sqlite`. A list/enrichment path that leaves a `Rows` cursor open and then performs another DB query will self-block on the only connection.

Observed case:

- `FetchPosts()` reads post rows, closes the main cursor, then enriches each post.
- `fetchPostMedia()` queried `post_media` and used `defer rows.Close()`.
- When a post had no `post_media` rows, it fell back to thumbnail media before the deferred close ran.
- `FetchPosts()` then called `fetchTargets()`, which tried another query while the `post_media` cursor still held the single connection.
- Result: `/api/posts` hung after restart/listing; published rows were still in SQLite but invisible to the UI.

## Minimal fix pattern

Close every `Rows` explicitly before any fallback return or nested query:

```go
rows, err := db.Query(`SELECT ...`)
if err == nil {
    items := make([]Item, 0)
    for rows.Next() { /* scan */ }
    rows.Close()
    if len(items) > 0 {
        return items
    }
}
return fallback
```

Do not use `defer rows.Close()` in helpers that may perform or trigger another DB query before returning.

## Regression shape

Use a test DB configured like production:

```go
db.SetMaxOpenConns(1)
db.SetMaxIdleConns(1)
```

Create a published post with a target but **no** `post_media` rows, then call `FetchPosts()` in a goroutine and fail if it does not return within ~2 seconds.

## Verification

- Targeted test: `go test ./internal/posts -run TestFetchPostsDoesNotDeadlockWhenPostHasNoMediaRows -count=1`
- Broader backend check: `go test ./internal/posts ./internal/comments ./internal/facebook ./internal/sync ./internal/models`
- Runtime probe with a real session cookie: `curl -m 10 -H 'Cookie: brand_session=<token>' 'http://127.0.0.1:8089/api/posts?limit=100'` should return JSON with published posts, not timeout.
