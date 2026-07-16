# WhatsApp-style single-video crop implementation

Use this when simplifying `apps/frontend/src/components/VideoCropModal.tsx` into a single live crop surface.

## Minimal implementation

- Keep the existing native `<video>` + CSS framing and FFmpeg-on-Apply/Download pipeline.
- Remove `edit`/`preview` mode state, tabs, separate result representation, and the right sidebar controls.
- Place the trim timeline above one output-ratio-clipped stage. That same stage handles playback, drag, pinch, and wheel zoom.
- Preserve Cancel as a no-processing action; preserve Download and Apply unless explicitly removed.
- Use the app's semantic/theme tokens for modal surfaces, text, borders, and primary actions. Provide light and `.dark` values; keep the media stage black.
- On mobile, use a near-full-screen single-column layout with `100dvh`, safe-area padding, no horizontal overflow, and at least 44px controls.

## Trim/play synchronization

Centralize boundary updates instead of setting React state alone:

```ts
const seek = (value: number) => {
  setNow(value)
  if (video.current) video.current.currentTime = value
}
const setTrimStart = (value: number) => {
  setStart(value)
  seek(value)
}
const setTrimEnd = (value: number) => {
  setEnd(value)
  if (video.current && video.current.currentTime >= value) seek(start)
}
```

Before Play, keep an in-range playhead unchanged, but reset an out-of-range playhead:

```ts
if (v.currentTime < start || v.currentTime >= end) v.currentTime = start
```

Keep `onTimeUpdate` and `onEnded` returning playback to `start`, not zero.

## Regression coverage

Write the focused test first and observe failure. Assert:

1. Old Edit/Result tabs and sidebar actions are absent.
2. Changing Trim start immediately changes `video.currentTime`.
3. Play from outside `[start, end)` starts at `start`.
4. Play from inside the range does not jump.

Then run:

```bash
pnpm exec vitest run src/components/VideoCropModal.test.tsx src/lib/video-crop-geometry.test.ts src/lib/video-processing.test.ts
pnpm typecheck
pnpm build
```

After deployment, verify the public lazy chunk is JavaScript and search all deployed chunks—not only `CreatePostPage-*.js`, because bundling can place `VideoCropModal` in a shared chunk—for a new marker such as `Live crop` and the absence of `Result preview`.
