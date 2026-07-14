# Edit & Retry should reuse New Post workflow and persisted crop state

Use this when improving failed-post retry/edit UX for SocialZen.

## Problem shape

Failed posts can currently open a reduced `EditPostPage.tsx` path instead of the full New Post workflow. That risks losing media crop/aspect/position and prevents editing platforms/accounts/publish mode with the same controls as create.

## Compact implementation direction

- Inspect first:
  - `apps/frontend/src/pages/posts/CreatePostPage.tsx`
  - `apps/frontend/src/pages/posts/EditPostPage.tsx`
  - `apps/frontend/src/components/PhotoCropModal.tsx`
  - `apps/backend-go/internal/posts/handler.go`
- Prefer reusing/extracting New Post form state and thumbnail UI rather than growing a separate edit-only experience.
- Persist image crop metadata per media item, ideally as normalized JSON on `post_media` (for example `crop_state TEXT`), so reopening is independent of display size.
- Make `PhotoCropModal` accept `initialCropState` and emit crop state with the cropped `File` on Apply.
- Initialize failed-post edit state from the saved post: media list + cropState, caption, target platforms, selected account/page, comment setting, publish mode, and schedule date/time.
- Thumbnails should match New Post behavior: click/Edit Image reopens the crop editor, `×` removes an item, and removing all media reveals the upload zone.
- Backend PATCH should accept the same logical edit payload as create: `caption`, `publishAt`, `platforms`, account IDs, `commentEnabled`, and full ordered `media[]` including `cropState`.
- For failed retries, reset failed post/targets to `SCHEDULED` without clobbering already `PUBLISHED` targets in partial-success posts.

## Pitfalls

- Re-cropping an already-cropped uploaded URL cannot recover pixels outside the cropped upload unless original media/source URL is also preserved. If full original-pixel recovery is required, add `originalUrl` or source-media persistence deliberately.
- Current `PhotoCropModal` has crop box/aspect state but no true zoom slider. Do not claim zoom preservation is complete unless a zoom control/state is added; otherwise map the requirement to preserved crop box/aspect and note the limitation.
- `post_media` schema changes require both production `internal/models/models.go` migration and test/legacy `db.go` migration.
- Do not rebuild all targets blindly on retry; preserve already-published targets for partial-success posts.

## Verification

- Frontend: `cd apps/frontend && pnpm typecheck && pnpm build`.
- Backend: `cd apps/backend-go && go test ./internal/posts && go build -o /tmp/socialzen-api .`.
- Manual QA: failed post opens with previous media/crop; clicking image opens cropper at previous crop; cancel loses nothing; removing last image shows uploader; platforms/accounts/publish mode/schedule remain editable; mobile and dark mode are usable.
