---
name: opendesign-remotion-video
description: Generate deterministic vertical videos from an OpenDesign-style clip-plan JSON using Remotion for sequencing and Three.js for visuals. Use when asked to combine OpenDesign layout/design planning with Remotion video generation.
---

# OpenDesign + Remotion Video

## Inputs

Require a clip-plan JSON containing project dimensions, fps, duration, palette, typography, and clips with `start`, `duration`, narration, on-screen text, and visual direction.

## Workflow

1. Store projects under `~/videos/<slug>`.
2. Treat OpenDesign as the design/layout layer: derive hierarchy, safe margins, palette, typography, scene numbering, text treatment, and transitions from the plan.
3. Use Remotion as the deterministic timeline/render layer. Composition settings must come from the JSON (`width`, `height`, `fps`, `total_frames`).
4. Use `@remotion/three` for Three.js content so rendering is frame-driven. Never use wall-clock animation or an independent `requestAnimationFrame` loop.
5. Prefer procedural geometry, lights, fog, and particles first. Add GLTF/Troika/GSAP/postprocessing only when the requested result actually needs them; Remotion's `interpolate()` and `spring()` are sufficient for most deterministic camera/text movement.
6. Keep each clip in a `<Sequence from={start * fps} durationInFrames={duration * fps}>`.
7. Typecheck, list compositions, and render a 3-second preview before the full render:

```bash
npx tsc --noEmit
npx remotion compositions src/index.tsx
npx remotion render src/index.tsx <Composition> out/preview.mp4 --frames=0-89 --codec=h264 --crf=24
```

8. Verify with `ffprobe`, extract a middle frame with FFmpeg, and visually inspect text bounds, contrast, 3D visibility, and cropping.
9. Fix preview defects before rendering the full video:

```bash
npx remotion render src/index.tsx <Composition> out/final.mp4 --codec=h264 --crf=22 --concurrency=2
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,r_frame_rate,pix_fmt -of json out/final.mp4
```

## Proven environment

- Node 24 ARM64 can be installed locally at `~/.local/node-24`; prepend it to `PATH`.
- System FFmpeg works for H.264 verification.
- Remotion downloads its compatible Chrome Headless Shell automatically.
- On TypeScript library declaration collisions from WebCodecs/Three, set `skipLibCheck: true`; keep project source strict.

## Quality gates

- Exact duration, fps, dimensions, and H.264 output match the plan.
- Text stays inside vertical safe margins and remains readable.
- Three.js objects are visibly lit, not merged into the background.
- All animation depends on `useCurrentFrame()`.
- Preview and full render commands complete successfully.

## Pitfalls

- `EffectComposer`/`UnrealBloomPass` and GLTF assets add render cost and failure surface; do not add them merely because they are listed as recommendations.
- Abstract dark materials require a front spot/key light in addition to rim and ambient lights.
- Procedural silhouettes can read as unintended objects. Render and inspect a representative still; prefer unmistakable geometry (for example a wireframe globe with latitude/longitude rings) over ambiguous capsule stacks.
- Full 90-second 1080x1920 Three.js renders can take several minutes; run them as a tracked background process with completion notification.
