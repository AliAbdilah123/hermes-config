# Photo crop root-cause triage

Use this when a user reports the crop modal still shows a dark/blank/faded area after a visual/CSS cropper fix.

## Goal

Prove which layer owns the problem before proposing another fix:

1. Uploaded image pixels
2. Crop box/math
3. Generated canvas/blob output
4. Preview rendering
5. Theme-specific CSS

Do not assume a dark-mode CSS cause just because the bug appears in dark mode.

## Evidence checklist

- Inspect the source/uploaded image metadata and pixels:
  - dimensions, mode, alpha extrema/bbox, mean RGB, dark/white pixel ratios
  - if the screenshot/crop selection already contains dark pixels, treat that as source/crop geometry evidence, not CSS evidence.
- Inspect `PhotoCropModal.tsx`:
  - `<img>` style for `object-fit`, `transform`, `filter`, `opacity`, `mixBlendMode`
  - crop surface dimensions: `width: displayW`, `height: displayH`
  - crop output path: `ctx.drawImage(img, srcX, srcY, srcW, srcH, 0, 0, outW, outH)`
- Inspect `globals.css`:
  - `.photo-crop-surface`
  - `.photo-crop-surface > img`
  - dark-mode selectors that might overmatch inline white backgrounds
- Inspect built/deployed assets, not just source:
  - production CSS includes `.photo-crop-surface` rules
  - production `PhotoCropModal-*.js` includes expected markers
  - JS asset returns `content-type: application/javascript`, not HTML
- If possible, compare light vs dark mode screenshots/pixels. If the canvas output itself contains the dark area, theme rendering is downstream/noise.

## Interpretation pattern

- If the crop box visibly includes a large dark/empty area and `drawImage` faithfully outputs that selected rectangle, the root is crop geometry/content bounds, not preview CSS.
- If the uploaded/generated image file already has dark pixels in the same region, preview rendering is not the source.
- If CSS explicitly resets `filter: none`, `opacity: 1`, and `mix-blend-mode: normal` on the crop image, do not keep adding generic CSS fixes without proving a CSS rule still wins.

## Why the prior dark-mode fix can fail

A fix that adds an isolated crop surface and resets image `filter`/`opacity`/`mix-blend-mode` only addresses visual rendering. It cannot change source pixels or the crop rectangle passed into `ctx.drawImage`. If the crop selection includes blank/dark padding, the generated image will preserve it.

## Smallest safe fix direction

Prefer changing crop initialization/ratio handling/content bounds in `PhotoCropModal.tsx` over another global CSS rule:

- initialize the crop box to actual visible image/content bounds when safe
- prevent ratio changes from creating a selection that mostly covers empty padding unless the user deliberately expands it
- optionally add a tiny visible-bounds detector for transparent or near-empty padding before initializing `box`

Keep CSS changes scoped; avoid broad dark-mode selectors that can alter media controls or image pixels.