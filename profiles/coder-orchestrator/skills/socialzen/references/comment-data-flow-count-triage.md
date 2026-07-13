# Comment data-flow count triage

Use when Instagram/Facebook comments or replies exist on the provider but are missing in SocialZen UI. Do **not** implement another fix until the loss layer is proven with counts.

## Required count chain

For one concrete `posts.id` / `post_targets.platform_post_id`, record:

1. **Meta API**
   - Top-level count from `/{media-or-post-id}/comments?limit=100` with cursor pagination.
   - Reply count by separately paging each top-level comment's reply edge:
     - Instagram: `/{ig-comment-id}/replies`
     - Facebook: `/{comment-id}/comments`
   - Capture provider errors separately from zero counts.
2. **Database**
   - `COUNT(*) FROM instagram_comments WHERE media_id=?`
   - Split `parent_id IS NULL` vs `parent_id IS NOT NULL`.
   - Inspect `instagram_comment_id` on both parent and reply rows; missing provider IDs can block reply sync/actions.
3. **API response**
   - Call `GET /api/instagram/comments/:postId?limit=25&offset=0` with a valid `brand_session` cookie.
   - Record HTTP status, bytes, elapsed time, top-level count, nested reply count, and `paging.hasMore`.
4. **Frontend fetch**
   - Check the Network response for the same endpoint; if API returns zero bytes or times out, frontend received `0` regardless of DB state.
5. **UI render**
   - Count rendered top-level comment items and nested replies separately.

## Critical SocialZen pitfall

`listComments()` can self-deadlock with production SQLite `SetMaxOpenConns(1)` if it keeps the top-level `rows` cursor open while calling helper queries such as `isLiked()` or `fetchReplies()` inside the loop. Symptom:

- DB has comment rows.
- Direct API call to `/api/instagram/comments/:postId` hangs/timeouts with `0 bytes received`.
- Frontend receives nothing and renders nothing.

Root fix direction: read top-level rows into memory, close `rows` explicitly, then run like/reply enrichment queries.

## Meta API zero vs local DB rows

Provider sync logs like this prove Meta returned no comments to the current token/API call, even when local DB has rows:

```text
comments sync instagram ... /<media-id>/comments ... count=0 next=false body={"data":[]...}
```

Treat this as a separate provider/token/permission/API-host problem from an API-response deadlock. Report both layers distinctly instead of saying the backend is fixed.
