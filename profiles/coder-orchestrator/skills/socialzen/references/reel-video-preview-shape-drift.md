# Reel/video preview shape drift

Use when SocialZen shows a blank/missing preview for a Reel or video after upload, selection, scheduling, or publishing.

## Triage order

1. Prove whether upload/backend capture worked before touching upload code:
   ```bash
   sudo sqlite3 /opt/socialzen/data/socialzen.db "
   SELECT p.id,p.user_id,p.type,p.status,p.instagram_account_id,p.media_thumbnail,p.error_message,
          p.publish_at,p.created_at,p.updated_at,
          GROUP_CONCAT(pt.platform||':'||pt.status||':'||COALESCE(pt.error_message,'')||':'||COALESCE(pt.platform_post_id,''),' | ') targets
   FROM posts p
   LEFT JOIN post_targets pt ON pt.post_id=p.id
   WHERE p.type IN ('REEL','VIDEO')
   GROUP BY p.id
   ORDER BY p.created_at DESC LIMIT 20;"

   sudo sqlite3 /opt/socialzen/data/socialzen.db "
   SELECT id,user_id,url,thumbnail_url,media_type,created_at
   FROM media ORDER BY created_at DESC LIMIT 10;"
   ```
2. Verify the media URL itself, origin and public/CDN:
   ```bash
   curl -sI http://localhost/projects/socialzen/media/<user>/<file>.mp4 | head -20
   curl -sI https://socialzen.ahsanworks.com/projects/socialzen/media/<user>/<file>.mp4 \
     | egrep -i 'HTTP|content-type|content-length|cache|accept-ranges'
   ```
   Expected for captured videos: `200`, `Content-Type: video/mp4`, nonzero `Content-Length`.
3. Check publish logs and target status separately:
   ```bash
   sudo journalctl -u socialzen.service --since '24 hours ago' --no-pager \
     | egrep -i 'publish|reel|video|media|error|fail|container|instagram' | tail -250
   ```
   If `post_targets` is `PUBLISHED` with `platform_post_id`, the publish path worked; don't debug provider upload.
4. Inspect API response shape consumed by React. `FetchPosts` must emit `media[].mediaType='VIDEO'` for `REEL`/`VIDEO`; otherwise the frontend may render an MP4 URL with `<img>` and show a blank preview.

## Fix pattern

Backend boundary (`internal/posts/handler.go`, `FetchPosts`):

```go
mediaType := "IMAGE"
if typ == "REEL" || typ == "VIDEO" {
    mediaType = "VIDEO"
}
media := []map[string]any{{"id": id + "_media_1", "position": 0, "mediaType": mediaType, "thumbnailUrl": thumbnail}}
```

Frontend preview components:

- Use `<video src={url} preload="metadata" muted playsInline>` for card thumbnails.
- Use `<video controls playsInline>` for detail modal and lightbox previews.
- Keep `<img>` for photos/carousels.

## Verification

- `go test ./internal/posts`
- `pnpm build`
- Deploy backend/frontend.
- Verify public JS asset is `application/javascript`, not cached HTML.
- Verify the MP4 URL returns `video/mp4`.

## Root-cause wording

If DB rows and MP4 HEAD checks are good, say: backend captured the media; the blank preview was frontend/API shape drift, not a failed upload.