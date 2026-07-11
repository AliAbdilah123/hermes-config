# Mobile crop gesture handling

When users report that mobile crop panning/trim dragging scrolls the whole page or feels laggy, fix the interaction boundary in the crop modal instead of changing upload/media processing.

## Root cause pattern

- `touch-action: none` on only the backdrop is not enough; mobile browsers still treat drags on the actual crop box/timeline as scroll gestures.
- `preventDefault()` on pointer down only is not enough; pointer move/up/cancel must also stop default scroll and event bubbling while dragging.
- Capturing the pointer on `e.target` can be fragile when the finger leaves a small handle. Capture on the stable container ref.
- React `setState` on every raw pointer event can make panning feel laggy; throttle visual drag state to one update per `requestAnimationFrame`.

## Minimal fix shape

For `PhotoCropModal.tsx` and similar crop surfaces:

1. Lock document scrolling while modal is mounted:
   - save/restore `document.body.style.overflow`
   - save/restore `document.body.style.touchAction`
   - set both to block page scroll during crop interaction.
2. Add `touchAction: "none"`, `overscrollBehavior: "contain"` or `"none"`, and `userSelect: "none"` to the actual interactive crop container, crop box, handles, video preview, and timeline.
3. In pointer handlers, call `e.preventDefault()` and `e.stopPropagation()` on down, move, up, and cancel paths when the interaction belongs to the crop UI.
4. Use `containerRef.current?.setPointerCapture(e.pointerId)` / `timelineRef.current?.setPointerCapture(e.pointerId)` rather than capturing on `e.target`.
5. For image crop pan/resize, stage the next box in a ref and commit `setBox()` inside `requestAnimationFrame`; cancel the pending frame on unmount.

## Verification

- Run `pnpm typecheck` and `pnpm build` from `apps/frontend`.
- Deploy built `dist/` to `/var/www/html/projects/socialzen/`.
- Verify the crop chunk is served as JavaScript, not cached SPA HTML:
  `curl -sI https://socialzen.ahsanworks.com/projects/socialzen/assets/<PhotoCropModal chunk>.js | grep -i content-type`
- Grep the deployed chunk for `touchAction`, `overscrollBehavior`, and `requestAnimationFrame` to prove the production bundle contains the fix.
