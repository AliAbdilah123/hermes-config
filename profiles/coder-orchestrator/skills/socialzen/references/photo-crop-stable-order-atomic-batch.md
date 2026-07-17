# Multi-image crop: stable order and atomic batch Apply

Use this when the New Post crop editor lets users switch among several uploaded photos and Apply is expected to process the whole set.

## State model

- Keep one stable ordered `File[]` representing upload/carousel order.
- Track the active editor selection separately by exact `File` identity or index.
- A thumbnail click changes only the active selection. It must not swap the selected file with position 1 or reorder the array.
- Keep per-image crop state in `WeakMap<File, CropState>` so duplicate uploads with identical metadata remain independent.
- Retain the loaded-file gate: clear transient geometry on `file` change and persist only when `loadedFileRef.current === file`.
- Removing the active image should select the nearest surviving image without reordering survivors.

## Atomic Apply

1. Save the active image's normalized crop state.
2. Materialize every ordered image from its own saved state.
3. Preserve output order exactly.
4. Validate every generated output against allowed aspect-ratio presets using a **proportional ratio tolerance**, not a fixed pixel tolerance. Preview-space integer rounding is amplified when normalized crop geometry is scaled back to the source image, so a valid crop can differ by several output pixels. A practical check is `abs(width / height - ratio) <= ratio * 0.01` (1% relative tolerance).
5. Keep a regression fixture that reproduces scaling amplification (for example `1272×660` for `1.91:1` and `1224×1536` for `4:5`) and a clearly invalid fixture outside tolerance.
6. If any output is invalid, return/upload zero files, keep the modal open, select the first invalid image, and show actionable copy.
6. Only after all outputs validate should the parent upload the complete batch.

Keep single-image callers backward compatible with a typed `onApply(File)` path; use a separate optional typed batch callback such as `onApplyBatch(File[])`. Never weaken the prop to `any` to support both shapes.

## TDD regression shape

- Two distinct `File` objects with the same name/type/timestamp select independently by identity.
- Selecting image N leaves the ordered array unchanged.
- Batch output order equals input order.
- One invalid ratio produces `{files: [], invalidIndex: N}`.
- Existing PNG transparency, loaded-file persistence, crop clamp, add/remove, typecheck, and production-build checks remain green.

## Verification

```bash
cd apps/frontend
pnpm exec vitest run src/components/PhotoCropModal.test.tsx
pnpm typecheck
pnpm build
```

After deployment, verify the new hashed `PhotoCropModal-*.js` and `CreatePostPage-*.js` assets return `application/javascript`, and grep the deployed crop chunk for the invalid-ratio message or another durable marker.
