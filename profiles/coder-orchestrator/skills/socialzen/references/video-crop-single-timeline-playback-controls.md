# Video Crop: Single Timeline and Playable Controls

Use when a single-surface video crop editor combines direct pointer manipulation with playback and trim controls.

## Failure pattern

Two regressions can appear even when unit tests and builds pass:

1. **Play/Pause does not respond** because the crop stage captures every bubbled `pointerdown`. A button nested inside that stage loses the normal pointer sequence when the parent calls `setPointerCapture()`.
2. **One video looks like it has three timelines** because Seek, Trim start, and Trim end are three full-width native range inputs, and each paints its own rail.

## Root fixes

### Separate timeline, playhead, and trim pointer ownership

A full-width transparent seek `<input type="range">` above the filmstrip can intercept every mouse/touch press, making any timeline interaction look like a playhead drag. Do not use that input as the visible timeline's pointer surface.

Use explicit ownership instead:

- **Timeline:** handle `pointerdown` on the filmstrip/selection background and seek once from `clientX`; do not capture the pointer or react to subsequent moves.
- **Playhead:** give the visible playhead its own touch-sized hitbox (about 24px around a 2px line), higher z-index, `touch-action: none`, and pointer capture only from its own `pointerdown`. Update seek during its captured moves.
- **Trim handles:** retain their own pointer capture and drag state. Stop bubbling or reject non-background targets so trim/playhead presses never invoke timeline seeking.
- **Accessible seek slider:** it may remain in the DOM for keyboard/screen-reader semantics, but make its full rail `pointer-events: none`; do not let its invisible box cover the timeline. If native trim sliders remain, expose pointer events only on their thumbs, while visible custom handles own direct manipulation.

Keep pointer-drag state separate (`playheadDrag`, trim start/end state). A timeline tap must not set playhead drag state.

### Keep crop gestures away from controls

Before pointer capture, ignore events originating from interactive descendants:

```tsx
const down = (event: React.PointerEvent) => {
  if ((event.target as Element).closest("button,input,a,select,textarea")) return
  event.currentTarget.setPointerCapture(event.pointerId)
  // start crop gesture
}
```

A dedicated gesture layer that excludes controls is also valid. Do not rely on `onClick` tests alone: direct synthetic clicks skip the browser's `pointerdown → capture → pointerup → click` sequence.

### Render one visual timeline

Keep one filmstrip/rail in the DOM and visually overlay:

- exactly two trim handles,
- one selection boundary,
- one playhead.

Seek, Trim start, and Trim end may remain separate accessible inputs, but their native rails must be transparent/visually hidden. Avoid stacking three unmodified native ranges; overlapping native hit areas are unreliable across browsers.

## TDD regression shape

1. Dispatch pointer events on Play and assert the crop stage does not call `setPointerCapture()`.
2. Complete the realistic pointer/click sequence and assert `video.play()` runs.
3. Give the filmstrip a deterministic bounding box; pointer-down on its background should seek to the calculated time, while a later pointer-move on the filmstrip should not move again.
4. Pointer-down/move on the dedicated playhead hitbox should seek continuously and must not trigger the filmstrip handler.
5. Drag each trim handle and assert only its trim boundary changes.
6. Assert exactly one visual filmstrip marker and two visible trim-handle markers exist.
7. Preserve accessible Seek, Trim start, and Trim end slider semantics without allowing invisible full-width rails to intercept direct manipulation.

After tests/build, verify the deployed marker in whichever lazy/shared chunk actually contains the editor; do not assume it lives in the Create Post chunk. Probe that public chunk for `Content-Type: application/javascript`.

## Visual acceptance gate

Before deployment, compare the actual rendered crop modal with the approved design—not only bundle markers or DOM text. A passing build cannot detect duplicated rails or misaligned handles. The accepted shape is one continuous WhatsApp-style strip, two handles on the same centerline, and one playhead. Verify light and dark themes and a phone viewport.
