# Instagram Graph API Comment Sync (Go + SQLite)

## Context
When a scheduling/publishing app needs to show real Instagram comments and metrics, not just local stubs. The Instagram Graph API returns `like_count` and `comments_count` on media objects, but **reading individual non-business comments often returns empty data** due to API permission limitations — only the business's own replies may be visible through the `/comments` edge.

## What Works vs What Doesn't

### Fetchable
- `GET /{ig-media-id}?fields=like_count,comments_count,media_type,permalink` — always returns counts
- `POST /{ig-media-id}/comments?message=...` — posting top-level comments (requires `instagram_business_manage_comments`)
- `POST /{ig-comment-id}/replies?message=...` — posting replies

### Not reliably fetchable (permission-limited)
- `GET /{ig-media-id}/comments?fields=id,text,username,timestamp` — often returns `{"data":[]}` even when `comments_count > 0`. This is a known limitation unless the app has Advanced Access approval for comment reading.

## Practical Architecture

### 1. Store Instagram Media ID on publish
When publishing succeeds, store `result.PostID` in `post_targets.platform_post_id`:
```go
app.DB.Exec(
    `UPDATE post_targets SET status='PUBLISHED', platform_post_id=?, published_at=?, updated_at=? WHERE id=?`,
    result.PostID, now, now, t.id,
)
```

### 2. Refresh metrics from Instagram
```go
func RefreshPostMetrics(app *models.App, postID string) error {
    // 1. Find Instagram media ID from post_targets JOIN posts
    // 2. Find account access_token from instagram_accounts
    // 3. Call GET /{ig-media-id}?fields=like_count,comments_count
    // 4. UPDATE posts SET likes=?, comments=? WHERE id=?
}
```

### 3. Post comments to Instagram (best-effort goroutine)
When a user creates a local comment:
```go
// Save locally first, then try Instagram in background:
go h.tryPostToInstagram(postID, parentID, commentID, message, userID)

func (h *Handler) tryPostToInstagram(...) {
    // 1. Find ig_media_id from post_targets
    // 2. Find access_token from instagram_accounts
    // 3. POST /{ig-media-id}/comments?message=... (top-level)
    //    or POST /{ig-comment-id}/replies?message=... (reply)
    // 4. Store returned Instagram comment ID for future reference
    // All errors are silently ignored — local comment is already saved
}
```

### 4. FindPost helper — JOIN query
```go
func findPostInstagramMediaID(app *models.App, postID string) (mediaID, accountID, userID string, err error) {
    err = app.DB.QueryRow(
        `SELECT pt.platform_post_id, pt.account_id, p.user_id
         FROM post_targets pt JOIN posts p ON p.id=pt.post_id
         WHERE pt.post_id=? AND pt.platform='instagram' 
           AND pt.status='PUBLISHED' 
           AND pt.platform_post_id IS NOT NULL AND pt.platform_post_id != ''`,
        postID,
    ).Scan(&mediaID, &accountID, &userID)
    return
}
```

## Pitfalls

1. **Comments endpoint returns empty**: The `/comments` edge on IG Media objects often returns `{"data":[]}` even when `comments_count` is non-zero. This is a Meta API permission issue — `instagram_business_basic` gives counts but `instagram_business_manage_comments` is needed to read individual comments, and even then it may require Advanced Access approval. Use `like_count` and `comments_count` for analytics; don't rely on reading individual comments from other users.

2. **Token field naming**: Despite being named `access_token_encrypted` in the schema, tokens may be stored as plaintext long-lived tokens if no actual encryption is implemented. Check the import flow before assuming encryption.

3. **Query requires user_id**: When looking up `instagram_accounts`, include `user_id` in the WHERE clause to scope to the correct user. Don't query by `id` alone.

4. **Reply posting needs Instagram comment ID**: To post a reply, you need the parent comment's Instagram ID (not the local DB ID). Store the returned Instagram comment ID when posting top-level comments so replies can target the right parent.

5. **Goroutine best-effort pattern**: Always save the local comment FIRST, then try Instagram in a goroutine. Don't let Instagram API failures block the local user experience.
