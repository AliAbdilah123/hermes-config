# Photo crop dark-padding RCA and fix pattern

Use when a user reports the photo crop preview/output has a large black/dark area above or around the real image content, especially after CSS visibility fixes did not help.

## Confirm before changing code

1. Inspect the uploaded/original image pixels and dimensions. Check whether alpha is present and whether the dark area is already in the pixels.
2. Inspect `apps/frontend/src/components/PhotoCropModal.tsx`:
   - preview `<img>` styles
   - crop-box `box` initialization
   - `ctx.drawImage(...)` source coordinates
3. Inspect `apps/frontend/src/globals.css` for crop-specific CSS:
   - `.photo-crop-surface`
   - `filter`
   - `opacity`
   - `mix-blend-mode`
   - light/dark selectors
4. Verify production bundle markers after deploy; SocialZen can serve stale Cloudflare-cached assets.

## RCA pattern

If CSS already forces the crop image to `filter:none`, `opacity:1`, and `mix-blend-mode:normal`, but the crop box visibly includes a big dark/empty band, the issue is crop geometry rather than theme rendering. `PhotoCropModal.handleApply()` uses canvas `drawImage(img, srcX, srcY, srcW, srcH, ...)`, so any dark padding inside `box` is preserved in the generated image.

## Small safe fix

Avoid another CSS-only fix. Initialize the crop box to obvious visible content when the source image has large transparent/dark padding. Keep it conservative:

- downsample to a small scan canvas;
- treat pixels as visible only when alpha is present and brightness is above a low threshold;
- only auto-crop if it trims a large band and still keeps a meaningful content area;
- otherwise keep the old full-image default.

When platform-specific aspect ratios are active, do not just set `h = w / ratio` on the detected box. Fit the ratio box centered inside the detected visible bounds (or full displayed image bounds) and clamp it there. Ratio button changes should also re-fit a clean centered crop for the selected ratio, otherwise the crop can stay anchored to a stale/bad position and appear as “auto cap/crop is not working.” A minimal helper shape is:

```ts
function fitCropBoxToRatio(bounds: Box, ratio: number): Box {
  const byWidthH = bounds.w / ratio
  if (byWidthH <= bounds.h) {
    const h = Math.round(byWidthH)
    return { x: bounds.x, y: Math.round(bounds.y + (bounds.h - h) / 2), w: bounds.w, h }
  }
  const w = Math.round(bounds.h * ratio)
  return { x: Math.round(bounds.x + (bounds.w - w) / 2), y: bounds.y, w, h: bounds.h }
}
```

Do not change drag/resize/pan math unless reproduction proves it is wrong.

## Verification

- `pnpm typecheck`
- `pnpm build`
- small pixel probe showing the problem image triggers the detector and a normal image does not
- deploy frontend and verify the deployed `PhotoCropModal-*.js` is `application/javascript` and contains the new marker (for example `willReadFrequently`)
