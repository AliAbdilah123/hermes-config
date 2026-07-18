# Edit / Edit & Retry existing-media controls

Use this when existing photos or videos disappear, cannot be opened, or lack per-item removal controls in `EditPostPage.tsx`.

## Root-cause checklist

- Do not gate the existing-media click handler to images only. Route `mediaType=IMAGE` to `PhotoCropModal` and `mediaType=VIDEO` to `VideoCropModal`.
- Render video items with `<video src={media.url ?? media.thumbnailUrl} muted playsInline preload="metadata">`; an MP4 passed to `<img>` appears blank.
- Put each existing media item in a positioned wrapper and add a separate accessible `type="button"` × control. Give it a label such as `Remove existing media 1` and a higher z-index than the preview button.
- Existing-media removal is a replacement operation: convert every remaining `post.media` item into the PATCH media DTO (`url`, `thumbnailUrl`, normalized `mediaType`, and a stable local key). Otherwise Save/Save & Retry either keeps the deleted item or drops unaffected siblings.
- When opening one existing carousel item for editing, prefill replacement state with all *other* existing items before uploading the edited result. The edited result is appended after Apply; unaffected siblings must not disappear.
- Replacement previews must branch on media type too; do not render all completed uploads as `<img>`.

## Crop/apply state invariant

Opening an existing item should set replace mode and retain unaffected siblings. Apply uploads the edited file and appends it to replacement state. Cancel/X must continue to use the established `usePreviousMedia()` path, restoring the original post media rather than saving a partial replacement.

## Minimal regression test

Keep a pure helper that maps existing `Post["media"]` into upload/PATCH-shaped media and optionally excludes one index. Test with one image plus one video and assert removing/editing the image retains the video URL, thumbnail, and `mediaType: "VIDEO"`.

Then run:

```bash
pnpm exec vitest run src/pages/posts/EditPostPage.test.tsx src/components/PhotoCropModal.test.tsx src/components/VideoCropModal.test.tsx
pnpm typecheck
pnpm build
```

After frontend deployment, verify the generated `EditPostPage-*.js` contains the new accessible removal marker and the public asset returns `Content-Type: application/javascript`.
