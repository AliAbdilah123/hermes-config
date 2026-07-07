# Facebook multi-photo feed publishing

When a Facebook Page post has 2+ photos, do **not** loop `POST /{page-id}/photos` with the default `published=true`. Each call becomes its own Page photo post.

Correct Graph API flow:

1. Upload each image as unpublished:
   `POST /{page-id}/photos` with `url=<image-url>`, `published=false`, and the Page token.
2. Collect each returned photo `id`.
3. Create one feed post:
   `POST /{page-id}/feed` with `message=<caption>` and repeated form keys:
   - `attached_media[0]={"media_fbid":"<photo_id_1>"}`
   - `attached_media[1]={"media_fbid":"<photo_id_2>"}`

SocialZen implementation shape:

- Keep single-photo behavior as normal `PublishPhotoPost(... published=true ...)`.
- For 2+ photos, add/reuse a helper like `PublishMultiPhotoPost` in `internal/facebook`.
- `publishFacebookPhotos` in `internal/posts/publisher.go` should filter out videos, build ordered photo URLs from `post_media`, and call the multi-photo helper once.
- Regression test should assert two image uploads use `published=false` and are followed by one `/feed` call containing `attached_media[0]` and the caption.

Root-cause symptom: user expects one gallery/carousel-style Facebook post, but sees N separate Facebook posts for N uploaded photos.