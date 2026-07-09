# Comment sync provider-ID and reply-mapping RCA

Use this when SocialZen comments/replies publish to Meta but do not appear in the app, or existing Instagram/Facebook comments are missing after opening the drawer.

## Durable findings

- Comment sync is impossible for an Instagram post unless `post_targets.platform_post_id` is present for the `instagram` target. `findPostInstagramMediaID()` returns no media ID when `platform_post_id` is empty, so `syncInstagramComments()` exits before fetching top-level comments or replies.
- Top-level comment publish needs only local post -> provider media mapping. Reply publish also needs local parent comment -> provider parent comment mapping (`instagram_comments.instagram_comment_id`). If the parent has no provider comment ID, reply publishing is skipped.
- Reply publish is currently async/best-effort. The HTTP API can return local success before Meta publish/provider-ID persistence has succeeded; errors in the async path can be silent unless logged.
- Current sync fetch shape includes nested replies via `fields=id,text,username,timestamp,like_count,replies{id,text,username,timestamp,like_count}` and upserts replies under the local parent ID returned by `localCommentID()`.
- Duplicate prevention depends on matching `(user_id, media_id, instagram_comment_id)` before creating `igcomment_<provider-id>`. If this matching regresses, synced replies can attach to a duplicate provider-parent row and look missing under the visible local parent.
- The API response intentionally fetches top-level rows (`parent_id IS NULL`) and nests replies via `fetchReplies()`. If replies exist in DB but not UI, inspect parent IDs and API shape before changing rendering.

## Triage queries

```bash
sqlite3 /opt/socialzen/data/socialzen.db "
SELECT c.media_id, p.status, pt.platform, pt.platform_post_id,
       COUNT(*) total,
       SUM(c.parent_id IS NULL OR c.parent_id='') top,
       SUM(c.parent_id IS NOT NULL AND c.parent_id!='') replies,
       SUM(c.instagram_comment_id IS NULL OR c.instagram_comment_id='') missing_provider
FROM instagram_comments c
LEFT JOIN posts p ON p.id=c.media_id
LEFT JOIN post_targets pt ON pt.post_id=p.id AND pt.platform='instagram'
GROUP BY c.media_id
ORDER BY MAX(c.created_at) DESC;"
```

```bash
sqlite3 /opt/socialzen/data/socialzen.db "
SELECT id, media_id, parent_id, instagram_comment_id, substr(message,1,60), created_at
FROM instagram_comments
ORDER BY created_at DESC
LIMIT 30;"
```

## Fix direction

- Add logging around publish comment, publish reply, missing post provider ID, missing parent provider ID, Meta returned ID, DB provider-ID update, sync fetch counts, save/update comment, save/update reply, DB query counts, and API response counts.
- Make provider publish result explicit: either publish synchronously before claiming provider success, or persist `sync_status` / `provider_sync_error` so local-only comments are visible as such.
- For replies, validate that the parent has `instagram_comment_id` before claiming provider-publish success; if missing, trigger a parent sync or return a clear recoverable state.
- Consider adding `provider_parent_comment_id` if cross-provider reconciliation needs explicit provider-parent tracking. Keep `parent_id` as the local FK.
- `fetchReplies()` should include `user_id` and preferably `media_id` filters, not only `parent_id`, even though local IDs are globally unique.

## Regression shape

Existing regression to keep:

```bash
cd /home/ubuntu/socialzen/apps/backend-go && go test ./internal/comments
```

Important case: local parent row has `instagram_comment_id='ig_parent'`; sync response returns the same parent plus nested reply `ig_reply`; assert only one parent row exists and `ig_reply.parent_id` equals the original local parent ID, not `igcomment_ig_parent`.
