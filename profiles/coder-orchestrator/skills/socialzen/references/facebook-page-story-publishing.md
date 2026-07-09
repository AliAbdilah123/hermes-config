# Facebook Page Story publishing

Use this when implementing/debugging SocialZen Facebook `STORY` targets.

## Graph API path used

- Image Story:
  1. `POST https://graph.facebook.com/{version}/{page-id}/photos`
     - `url=<public image URL>`
     - `published=false`
     - `access_token=<Page token>`
  2. Read returned `id` as the unpublished photo id.
  3. `POST https://graph.facebook.com/{version}/{page-id}/photo_stories`
     - `photo_id=<photo id>`
     - `access_token=<Page token>`

- Video Story:
  - `POST https://graph.facebook.com/{version}/{page-id}/video_stories`
    - `file_url=<public video URL>`
    - `access_token=<Page token>`

## SocialZen wiring pattern

- Keep `STORY` as a first-class scheduled post type through the existing lifecycle.
- In `internal/posts/publisher.go`, route `platform=facebook` + `type=STORY` after fetching active `facebook_pages` Page token.
- Reuse ordered `post_media` via the existing media helper, not `posts.media_thumbnail` alone.
- Enforce exactly one Facebook Story media item. Return clear failures for missing or multiple media.
- Keep Instagram Story publishing unchanged: Instagram uses `media_type=STORIES` with `image_url` or `video_url` based on media type.

## Tests to preserve

- A Facebook package unit test should assert image Story does `/photos` with `published=false`, then `/photo_stories` with `photo_id`.
- A Facebook package unit test should assert video Story uses `/video_stories` with `file_url`.
- A posts package unit test should assert Facebook Story rejects zero media and multiple media.

## Deploy reminder

After backend changes: `go test ./internal/posts ./internal/facebook`, `go build -o /tmp/socialzen-api .`, install to `/opt/socialzen/socialzen-server`, restart `socialzen.service`, and verify public app/asset content type. `go test ./...` may expose unrelated root-suite drift; do not hide it, but targeted packages are the required regression signal for this path.
