# Instagram carousel multi-media publishing

## Symptom

A user uploads a carousel with multiple media items (for example 2 photos + 1 video), but Instagram publishes only the first photo.

## Root cause pattern

Do not treat `posts.media_thumbnail` as the post's media source for carousel publishing. That column is only a thumbnail/legacy single-media pointer. If the create/edit API only stores the first item's `thumbnailUrl`, the publisher has no durable record of the remaining carousel items and can only create one Instagram media container.

## Durable fix shape

1. Persist every selected media item in a post-scoped table such as `post_media`:
   - `post_id`
   - `url`
   - `thumbnail_url`
   - `media_type` (`IMAGE` or `VIDEO`)
   - `position`
2. Ensure frontend create/edit payloads include each uploaded media item's real `url`; `r2Key` + `thumbnailUrl` is not enough.
3. Fetch `post_media` in the Instagram publisher for `CAROUSEL_ALBUM`, ordered by `position`.
4. For Instagram Graph carousel publishing:
   - create one child container per media item with `is_carousel_item=true`
   - image child: `image_url=<public-url>`
   - video child: `media_type=VIDEO`, `video_url=<public-url>`
   - wait for child containers as needed
   - create parent container with `media_type=CAROUSEL` and `children=<comma-separated child ids>`
   - publish the parent container via `/media_publish`
5. Keep a fallback to legacy `media_thumbnail` for old single-media posts or old rows without `post_media`.

## Verification

- Unit-test the generated Instagram form values for image child, video child, and carousel parent.
- Run `go test ./internal/posts`.
- Rebuild/deploy backend and frontend.
- Verify the migration created `post_media` in the live DB after service restart.

## Pitfall

Already-published one-photo carousel posts cannot be expanded in-place by Instagram. The fix applies to new/retried posts that still have all media stored; already published bad posts must be recreated/reposted.