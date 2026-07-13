# Comment list API deadlock with SQLite single connection

## Symptom

`GET /api/instagram/comments/:postId` times out with zero bytes even though `instagram_comments` has the expected top-level comments and replies. The frontend receives no JSON and renders no comments.

Example evidence shape:

```text
SQL: total=2 top=1 replies=1
API before fix: curl timeout after 25s, 0 bytes
```

## Root cause

Production SocialZen intentionally uses SQLite with `SetMaxOpenConns(1)`. The comments list handler queried top-level rows and kept the `Rows` cursor open via `defer rows.Close()`, then called nested DB helpers (`isLiked`, `fetchReplies`) while iterating/building the response. `fetchReplies` also kept its own `Rows` open while calling `isLiked` for each reply.

With one SQLite connection this self-blocks: open cursor holds the only connection, nested query waits forever for that same connection.

## Minimal fix pattern

1. Read all top-level rows into a small slice.
2. Close the top-level `Rows` explicitly.
3. Then build the response and call `isLiked` / `fetchReplies`.
4. In `fetchReplies`, read reply rows into a slice, close `Rows`, then call `isLiked` while building reply DTOs.
5. Do **not** change Meta sync logic in this fix; this is DB-to-API response behavior only.

Pseudo-shape:

```go
rows, err := db.Query(`SELECT ...`)
// scan into []row
rows.Close()

for _, row := range rowsSlice {
    dto := map[string]any{
        "liked": h.isLiked(userID, row.id),
        "replies": h.fetchReplies(userID, row.id),
    }
}
```

## Regression test shape

Use a test DB configured like production:

```go
db.SetMaxOpenConns(1)
db.SetMaxIdleConns(1)
```

Create:

- one top-level comment
- one reply under it
- empty `comment_likes`

Call `listComments` in a goroutine and fail if it does not return within ~2 seconds. Assert `200` and the response includes both top-level comment and reply.

## Verification checklist

After deploying backend:

```bash
# 1. SQL counts
sqlite3 /opt/socialzen/data/socialzen.db "
SELECT COUNT(*) total,
       SUM(parent_id IS NULL) top,
       SUM(parent_id IS NOT NULL) replies
FROM instagram_comments WHERE media_id='<post_id>';
"

# 2. API counts using a valid brand_session cookie
curl -m 10 -H 'Cookie: brand_session=<token>' \
  'http://127.0.0.1:8089/api/instagram/comments/<post_id>?limit=25&offset=0'
```

Count API top-level comments plus nested `replies`. Frontend received count is the API JSON count; UI rendered count can be proved with a focused `CommentList` render test that mocks the same JSON and asserts both comment and reply text are in the document.

Recommended commands:

```bash
go test ./internal/comments -run TestListCommentsDoesNotDeadlockWithRepliesAndSingleSQLiteConnection -count=1
go test ./internal/comments ./internal/posts
pnpm exec vitest run src/components/comments/CommentList.test.tsx
pnpm typecheck && pnpm build
```
