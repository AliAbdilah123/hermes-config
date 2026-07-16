# Modern video crop experience

Use this when implementing or revising `VideoCropModal.tsx` from an approved crop-editor design.

## Smallest architecture

- Keep interactive editing CSS/native-video only; load and run FFmpeg only for Apply or Download.
- Store one normalized framing state: `{ x, y, zoom }`, plus trim start/end and fixed output ratio.
- Put pure geometry in a small tested module. Cover contain-fit, ratio frame, bounded pan, pinch/zoom math, and bounded even FFmpeg coordinates.
- Use `ResizeObserver` so the source initially fits both available width and height with every edge visible.
- Edit mode shows the whole source and crop chrome. Preview mode must clip to the exact output frame and hide borders, dimming, handles, and editor overlays.
- Apply and Download must call the same processing function and consume the same geometry snapshot used by Preview.
- Preserve the no-change return path and trim-only stream-copy path.
- Never silently return the original file after an FFmpeg error; show an actionable error and leave the editor open.

## Interaction requirements

- One pointer pans; two pointers pinch; wheel and a labeled range input zoom.
- Clamp pan and zoom so the output frame is always covered.
- Playback supports play/pause, seek, mute, and replay. At trim end or native `ended`, seek to trim start before replay/loop.
- Cancel/X performs no processing or upload.
- Under 640px, use a full-screen editor with safe visible controls, no horizontal overflow, and at least 44px targets.
- Keep dialog semantics, labels, focus visibility, and reduced-motion behavior.

## TDD and verification

1. Add geometry tests before the module and run them to observe the expected missing-module/behavior failure.
2. Implement the minimum geometry and rerun focused geometry plus existing video-processing tests.
3. Run `pnpm typecheck` and `pnpm build`.
4. Inspect the built chunk for distinctive editor copy such as `Trim & Crop Video` and `Download`.
5. Deploy from `apps/frontend/dist/` to `/var/www/html/projects/socialzen/` (the build output is not at the repository root).
6. Verify local and public JS return `application/javascript`, then commit and push.

## Review pitfall

A passing build is insufficient. Before deployment, compare the implementation to the approved visual artifact. In particular, do not accidentally remove secondary actions such as Download, and do not call a mode “Preview” if it merely hides the crop border while still displaying the full un-clipped stage.
