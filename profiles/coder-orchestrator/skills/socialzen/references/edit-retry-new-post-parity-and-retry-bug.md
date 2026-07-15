# Edit & Retry parity + Save & Retry retry bug

Use this when planning or implementing SocialZen failed-post retry/edit flows.

## Context

Failed posts should reopen in an edit flow that is equivalent to New Post: same platform/account selectors, publish mode controls, media thumbnails, upload queue, and crop editor. The user specifically wants original crop/aspect/position/zoom state preserved when editing failed media.

## Key code boundaries

- Frontend New Post source of truth: `apps/frontend/src/pages/posts/CreatePostPage.tsx`
- Current failed/scheduled edit page: `apps/frontend/src/pages/posts/EditPostPage.tsx`
- Crop editor: `apps/frontend/src/components/PhotoCropModal.tsx`
- Backend post create/patch: `apps/backend-go/internal/posts/handler.go`
- Publisher/enqueue lifecycle: `SCHEDULED -> PUBLISHING -> PUBLISHED/FAILED`

## Important bug pattern

`EditPostPage.tsx` can skip PATCH entirely when no visible fields changed:

```ts
if (Object.keys(body).length === 0) {
  navigate("/app/posts")
  return
}
```

For failed posts this means pressing **Save & Retry** may only navigate away. It never resets `posts.status` or failed `post_targets.status` to `SCHEDULED`, so enqueue/publisher has nothing to repost.

Fix direction:
- For failed posts, always send a retry PATCH even if no visible fields changed.
- Include a clear intent field such as `retry: true`, or send the full New Post-equivalent payload.
- Backend must reset `posts.status='SCHEDULED'`, clear parent error, and reset retryable failed targets to `SCHEDULED`.
- Add regression: failed post + failed target + unchanged retry PATCH returns post `SCHEDULED` and target `SCHEDULED`.

## Backend PATCH pitfalls

- Do not use non-empty value checks as the only update signal:
  - `if v := models.Str(in["caption"]); v != ""` prevents clearing caption.
  - `if mediaArr, ok := in["media"].([]any); ok && len(mediaArr) > 0` ignores intentional empty media arrays, so remove-all-media cannot be validated/persisted correctly.
- Treat key presence as the update signal, then validate whether the supplied value is allowed.
- Media-required post types/platforms should reject invalid empty media explicitly with 400 instead of silently keeping old media.

## Crop-state persistence direction

Current `PhotoCropModal` keeps crop state internally only (`preset`, crop `box`, natural/display dimensions). To preserve crop across Edit & Retry:
- Add a normalized frontend crop state (`preset`, normalized box `{x,y,w,h}`, natural dimensions, optional zoom default `1`).
- Let `PhotoCropModal` accept `initialCropState` and emit crop state with the cropped file.
- Persist nullable `crop_state TEXT` on `post_media` in both production and test migration paths.
- Return `cropState` with each media item in post DTOs.

## UX acceptance points

- Failed post Edit & Retry should visually match New Post.
- Image thumbnail click and/or an `Edit Image` button opens the same crop editor. A minimal implementation can fetch the existing media `url`/`thumbnailUrl` as a Blob, wrap it in a `File`, set `mediaMode='replace'`, then upload the cropped result through the existing replacement path.
- Failed-post Edit & Retry should expose the same Post Now / Schedule choice as New Post; for `Post Now`, PATCH `publishAt` to `Date.now()+35s` so retry goes through the normal scheduler/enqueue path.
- Thumbnail `×` removes media; if all media is removed, show the same upload fallback.
- Caption, platform(s), selected account(s), Post Now/Schedule, schedule date/time, and editable settings remain editable.
- Cancel/reopen does not lose current form or crop state.
- Verify light/dark and mobile layouts, especially crop controls.
