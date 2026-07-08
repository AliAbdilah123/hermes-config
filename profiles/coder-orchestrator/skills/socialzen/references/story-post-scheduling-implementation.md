# Story post scheduling implementation

Use this when implementing or extending SocialZen Story support after a story-posting PRD/review artifact is approved.

## Backend behavior

- Add `STORY` as a first-class post type without changing the existing scheduled-post lifecycle (`SCHEDULED` → `PUBLISHING` → target publish result → parent status).
- Instagram automated publishing should use the existing media container workflow:
  - `POST /{ig-user-id}/media`
  - `media_type=STORIES`
  - choose URL field by actual media item type:
    - image story: `image_url=<public-url>`
    - video story: `video_url=<public-url>`
  - poll container status, then `POST /{ig-user-id}/media_publish`.
- Story container polling should use the longer Reel/video timeout window, not the short image timeout, because video stories can need processing time.
- Facebook Story automated publishing is not proven in SocialZen yet. If a `STORY` target is Facebook, return a clear target-level failure such as `Facebook Story automated publishing is not available yet; manual posting required` instead of silently falling back to a feed post.

## Frontend behavior

- Include `STORY` in create/edit post type unions and labels.
- Create flow should show Story as a post type alongside Photo/Reel; keep Instagram carousel availability rules unchanged.
- Story uploads should accept exactly one image or video and present 9:16 guidance.
- Edit flow should allow replacing story media with one image or video.
- Add `STORY` to shared frontend post-type unions used by Calendar/Dashboard/Post cards if they type-narrow post data.
- If PostHog/event type unions exist, add `story` rather than mapping stories to `reel` or `photo`.

## Regression tests

Targeted backend tests should cover:

```go
form := instagramMediaForm("https://cdn.test/story.mp4", "caption", "STORY", "VIDEO", false)
// media_type == STORIES, video_url set, image_url empty

imageForm := instagramMediaForm("https://cdn.test/story.jpg", "caption", "STORY", "IMAGE", false)
// media_type == STORIES, image_url set, video_url empty

// STORY timeout >= REEL timeout
```

Then run at least:

```bash
cd apps/backend-go && go test ./internal/posts && go build -o /tmp/socialzen-api .
cd apps/frontend && pnpm typecheck && pnpm build
```

Full `go test ./...` may expose unrelated root-package drift; do not block a scoped story implementation when the touched package tests and builds pass, but report unrelated failures clearly.