# Photo crop transparent PNG output

Use this when the Photo Crop modal shows a solid black/dark rectangle for transparent PNG areas even though the source upload is valid.

## Root cause pattern

Check the canvas export path before adding CSS fixes. A valid transparent PNG can be rendered correctly in the modal but lose alpha if the crop output is always encoded as JPEG:

```ts
offscreen.toBlob(..., "image/jpeg", 0.92)
new File([blob], name, { type: "image/jpeg" })
```

JPEG has no alpha channel. Transparent pixels from the canvas are flattened by the browser encoder and can appear black/dark in downstream previews, uploads, or theme surfaces. This is an output-generation bug, not a dark-mode/rendering bug.

## Fix pattern

- Preserve PNG uploads as PNG crop outputs:
  - `outputType = file.type === "image/png" ? "image/png" : "image/jpeg"`
  - use `.png` extension for PNG output
  - pass no quality argument for PNG
- Keep JPEG/non-transparent photos as JPEG with the existing quality setting.
- Add a small pure helper such as `cropOutputFormat(inputType)` and a unit test that asserts `image/png` returns `image/png`, `.png`, and `quality: undefined`.
- Keep the real preview image scoped and unmodified (`filter: none`, `opacity: 1`, `mix-blend-mode: normal`).

## UI cleanup that pairs safely with the fix

- The crop canvas shell can use a neutral light checkerboard/gray background so transparent pixels are visible.
- Dim outside the selected crop area with overlay rectangles; do not hide or clip the unselected image.
- Use rounded white/off-white handles with a 2px accent border and shadow. In SocialZen, `rgb(254,254,254)` intentionally avoids broad dark-mode fallback selectors that target pure white inline styles.
- If users reopen the same pending file, preserve crop box as normalized coordinates keyed by file identity (`name:size:lastModified`) so auto-fit does not reset their crop.

## Verification

Run:

```bash
cd /home/ubuntu/socialzen/apps/frontend
pnpm exec vitest run src/components/PhotoCropModal.test.tsx
pnpm typecheck
pnpm build
```

After deploy, verify the built crop bundle contains `image/png` and the neutral-canvas marker, and that the asset returns `application/javascript` from the public domain.