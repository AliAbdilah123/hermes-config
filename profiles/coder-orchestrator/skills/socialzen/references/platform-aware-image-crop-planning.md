# Platform-aware image crop planning

Use when planning or implementing New Post image cropping for SocialZen across Instagram, Facebook, and Threads.

## Current SocialZen flow to inspect first

- Frontend create flow: `apps/frontend/src/pages/posts/CreatePostPage.tsx`
  - `handleFiles()` filters selected files by `postType` and opens a crop modal before upload.
  - `advanceCropQueue()` uploads the resolved/cropped file to `/api/posts/media`.
  - Submit sends `mediaThumbnail` plus ordered `media[]` to `/api/posts`.
- Existing image cropper: `apps/frontend/src/components/PhotoCropModal.tsx`
  - Already supports presets `1:1`, `4:5`, `1.91:1`, and `free`.
  - Existing `free`/custom ratio behavior can violate platform-locked-ratio requirements because `PRESET_RATIOS.free` is `null`.
  - Preserve mobile pointer/touch handling and the off-white crop handle workaround (`rgb(254,254,254)`) so dark-mode global fallbacks do not hide handles.
- Backend upload/create handlers: `apps/backend-go/internal/posts/handler.go`
  - `/api/posts/media` saves the uploaded file and infers `mediaType`.
  - `/api/posts` persists ordered `post_media` rows.
  - No existing dimension/aspect-ratio validation unless explicitly added.

## Official-doc research baseline

Check Meta docs again at implementation time, but this is the planning baseline:

- Instagram Content Publishing docs: image publishing uses public URLs and supports image/video/reel/story/carousel containers.
- Instagram API-published feed images should be JPEG; extended JPEG variants such as MPO/JPS are not supported.
- Instagram feed-safe ratios: `4:5` portrait through `1.91:1` landscape, including `1:1` square.
- Instagram carousel supports up to 10 items; carousel images are cropped based on the first image, defaulting to `1:1` if not controlled.
- Stories should use `9:16` as the safe/default image crop.
- Facebook Page photos are more flexible, but when cross-posting with Instagram the stricter Instagram rules should win.
- Threads support should be centralized in the same requirements module; verify latest Threads publishing endpoint docs before finalizing exact limits.

## Recommended architecture

1. Add a small frontend requirements module, e.g. `apps/frontend/src/lib/media-requirements.ts`.
   - Define platform/post-type requirements and allowed crop presets.
   - Return default preset, warnings, and blocking incompatibility messages.
   - Keep requirements as constants/functions, not DB-configurable rules.
2. Make `PhotoCropModal` accept dynamic locked presets.
   - New Post should not pass `free` when platform publishing requires locked ratios.
   - If custom W:H remains, store it as a real locked ratio value, not as `free`.
   - Add `9:16` support for stories.
3. Keep cropping browser-side via Canvas for V1.
   - Output JPEG for Instagram compatibility.
   - Use a safe default output longest side such as 1080px unless the user approves exposing an advanced Max PX field.
4. Add backend safety only with stdlib where possible.
   - Use Go `image.DecodeConfig` for basic image validation/dimensions if needed.
   - Do not add server-side cropping or new image dependencies unless there is a clear reason.

## UX rules

- New Post crop box must always remain locked to the selected ratio.
- Moving the box never changes ratio; resizing recalculates the opposite dimension and clamps inside image bounds.
- Auto-crop should choose the largest centered crop that fits the selected ratio, optionally starting from obvious visible-content detection while preserving ratio.
- Show compatibility copy near the media uploader only when it does not duplicate modal controls. Do **not** show crop ratio choices as a persistent panel on the New Post form before upload; ratio choices belong inside the crop/edit modal.
- In the modal, ratio buttons should immediately re-fit the crop box for the chosen ratio. Use a centered/clamped fit helper rather than resizing from a stale box corner.
- Show compatibility copy near the media uploader:
  - green: already valid / will be cropped correctly;
  - yellow: crop needed or carousel ratio caveat;
  - red: selected platform/post type cannot use this media.
- For Instagram carousel, warn or force one shared ratio for the queue; ask the user which behavior they want before implementation.

## Plan-first/public artifact requirement

For SocialZen crop-feature plans, produce a public HTML review artifact under `/prd/socialzen/<slug>.html` before implementation. Include an explicit implementation gate and open questions; do not treat answers to design/UX questions as implementation permission unless the user explicitly says to implement/deploy.
