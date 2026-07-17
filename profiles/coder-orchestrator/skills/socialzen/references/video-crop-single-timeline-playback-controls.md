# Video Crop: Single Timeline and Playable Controls

Use when a single-surface video crop editor combines direct pointer manipulation with playback and trim controls.

## Failure pattern

Two regressions can appear even when unit tests and builds pass:

1. **Play/Pause does not respond** because the crop stage captures every bubbled `pointerdown`. A button nested inside that stage loses the normal pointer sequence when the parent calls `setPointerCapture()`.
2. **One video looks like it has three timelines** because Seek, Trim start, and Trim end are three full-width native range inputs, and each paints its own rail.

## Root fixes

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
3. Assert exactly one visual filmstrip marker exists.
4. Assert exactly two visible trim-handle markers exist.
5. Preserve three accessible slider semantics (Seek, Trim start, Trim end) without three visible rails.

## Visual acceptance gate

Before deployment, compare the actual rendered crop modal with the approved design—not only bundle markers or DOM text. A passing build cannot detect duplicated rails or misaligned handles. The accepted shape is one continuous WhatsApp-style strip, two handles on the same centerline, and one playhead. Verify light and dark themes and a phone viewport.
