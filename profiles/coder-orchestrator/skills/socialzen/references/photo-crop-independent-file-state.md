# Photo crop independent file state

When the New Post photo crop dialog lets users switch between multiple uploaded images, crop state must be tied to the exact uploaded `File` object, not a derived key like `name:size:lastModified`.

## Symptom

- Upload multiple images, switch left → right → left repeatedly.
- The crop box/output keeps getting smaller or transformations appear to accumulate.
- Uploading the same image multiple times can reproduce it because duplicate files share the same derived key.

## Root cause

A module-level map keyed by `file.name:file.size:file.lastModified` makes duplicate file uploads share one crop state. Switching thumbnails rehydrates and rewrites the same stored normalized crop box/preset, so one file's crop can mutate another's crop.

## Fix pattern

- Store crop state in a `WeakMap<File, CropState>` keyed by the actual `File` object identity.
- Persist the full per-file state: normalized crop box, aspect preset, max-px setting, custom ratio fields if available.
- On image load, restore from the `WeakMap<File, CropState>` and scale the normalized box to the current display size exactly once.
- Keep selection/removal logic in the parent queue: removing the current pending file should select the nearest remaining queued file or clear pending crop state when none remain.
- Add a tiny regression around normalized crop restoration to prove repeated restores are idempotent.

## UI polish pattern

- Put the dotted editor-style background on the crop canvas panel, not on the image element.
- Light mode: off-white/gray subtle dot grid. Dark mode: charcoal subtle dot grid.
- Thumbnail strip should be horizontally scrollable, with active-state ring/shadow, smooth hover transitions, and a floating remove `×` per thumbnail.

## Verification

Run:

```bash
cd apps/frontend
pnpm exec vitest run src/components/PhotoCropModal.test.tsx
pnpm typecheck
pnpm build
```

After deploy, grep the built artifacts for durable markers such as `WeakMap`, `photo-crop-thumb-remove`, and `photo-crop-canvas-panel`, then verify the public JS asset returns `application/javascript`.
