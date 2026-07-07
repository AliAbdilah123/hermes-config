# Facebook carousel/media publishing in SocialZen

## Symptom

Facebook Page posts publish without the uploaded media, or a `CAROUSEL_ALBUM` only sends the first image/video even though `post_media` contains all uploaded items. Reels may fall through to a text/default Facebook post if only `VIDEO` is handled.

## Root cause pattern

Instagram publishing uses `post_media` (`url`, `media_type`, `position`) to build the real media list, but Facebook publishing can drift back to using only `posts.media_thumbnail`. `media_thumbnail` is a single preview/fallback, not the source of truth for carousel media.

## Fix pattern

- Read media from `post_media` ordered by `position`, falling back to `posts.media_thumbnail` only when no rows exist.
- For Facebook single-photo posts, call `/photos` with the first media URL.
- For Facebook video and reel posts, call `/videos` with `file_url` from the first media URL. Include both `VIDEO` and `REEL` in the dispatch.
- For Facebook `CAROUSEL_ALBUM`, publish every media item in order:
  - `media_type=IMAGE` → Facebook `/photos` with `url`
  - `media_type=VIDEO` → Facebook `/videos` with `file_url`
- Facebook Page API does not provide the same direct carousel-child-container flow as Instagram; the pragmatic fallback is ordered per-item publishing unless product requirements demand a different Facebook-specific feed/link carousel implementation.

## Regression tests

Add/keep focused tests that prove:

1. Facebook media collection returns every `post_media` row, public-URL-normalized, not just `media_thumbnail`.
2. Mixed carousel publishing issues one `/photos` call for image items and one `/videos` call for video items with the correct URL parameters.

Targeted verification:

```bash
cd apps/backend-go
go test ./internal/posts
go build -o /tmp/socialzen-api .
```

If `go test ./...` fails in unrelated root tests, report that separately; do not block the targeted Facebook publishing fix when `./internal/posts` and build pass.
