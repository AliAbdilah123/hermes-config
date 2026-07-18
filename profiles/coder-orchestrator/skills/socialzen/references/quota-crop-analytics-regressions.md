# Quota, crop queue, and analytics media regressions

## Free-tier quota migration

When quota enforcement uses an authoritative `post_quota` reservation ledger, creating the table is insufficient for an existing installation. Historical `PUBLISHED` posts can be visible in usage counts while absent from admission counts, allowing an 11th free-tier post.

After creating `post_quota`, run an idempotent backfill in **both** migration paths:

```sql
INSERT OR IGNORE INTO post_quota(post_id,user_id,state,created_at,updated_at)
SELECT id,user_id,'CONSUMED',?,?
FROM posts
WHERE status='PUBLISHED';
```

Regression shape: insert 10 published posts without quota rows, rerun migration, and assert the next reservation returns `ErrPostQuotaExceeded`. After deployment, verify there are no published posts missing ledger rows:

```sql
SELECT COUNT(*)
FROM posts p
WHERE p.status='PUBLISHED'
  AND NOT EXISTS (SELECT 1 FROM post_quota q WHERE q.post_id=p.id);
```

Keep quota admission backend-enforced. Do not fix only the dashboard/Settings usage display.

## Atomic image crop queue vs sequential video queue

Create Post has two different queue semantics:

- Image crop applies atomically to the complete ordered image batch, so the queue passed to `PhotoCropModal.files` must include the active first image.
- Video crop processes one file at a time, so its remaining queue must exclude the active first video.

A shared `const [first, ...rest]` followed by `setCropQueue(rest)` breaks a single-image crop: `PhotoCropModal` receives `files=[]`, materializes zero files, closes, and uploads nothing. Use a tiny tested helper that returns all files when the first file is an image and `files.slice(1)` otherwise. Test both one-image and video-plus-remaining-file cases.

## Analytics thumbnails for legacy published posts

Analytics insight cards can render images only if the backend DTO propagates a primary media URL. Select the first `post_media` row by `(position,id)`, then fall back to legacy `posts.media_thumbnail`.

Empty strings require `NULLIF`; ordinary `COALESCE` treats `''` as present and blocks fallback:

```sql
COALESCE(
  (SELECT COALESCE(NULLIF(pm.thumbnail_url,''), NULLIF(pm.url,''))
   FROM post_media pm
   WHERE pm.post_id=p.id
   ORDER BY pm.position,pm.id LIMIT 1),
  NULLIF(p.media_thumbnail,''),
  ''
)
```

Regression shape: a published post with `post_media.thumbnail_url=''` and a valid `post_media.url` must return the URL; after deleting `post_media`, it must return the legacy thumbnail. Mapping-only tests do not cover SQL selection/fallback bugs.

## Compact verification

Run targeted regression tests first, then frontend typecheck/build and backend package tests/build. Deploy backend and frontend, verify service health, confirm the public hashed JavaScript asset is `application/javascript`, and commit/push only the scoped files when the worktree contains unrelated changes.
