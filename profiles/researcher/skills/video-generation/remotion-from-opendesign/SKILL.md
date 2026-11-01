---
name: remotion-from-opendesign
description: Produce vertical short-form videos (TikTok/Reels/Shorts) by combining OpenDesign's design-system layer with a deterministic Remotion render timeline. Use when asked to build motion-graphics clips from a clip-plan JSON, a lecture/podcast transcript, or source footage, especially premium editorial/kinetic-typography layouts (presentation frame + speaker inset + burned-in subtitles).
---

# Remotion from OpenDesign

Two layers, one pipeline:

- **OpenDesign = design layer.** Supplies the visual identity: palette, typography
  scale, spacing rhythm, safe margins, editorial hierarchy. Never invent a look
  when a design system is available.
- **Remotion = timeline layer.** Supplies determinism: every frame is a pure
  function of `useCurrentFrame()`. No wall-clock animation, no rAF loops.

## Inputs

- Clip plan JSON: `id`, `part`, `title`, `kicker`, `hook`, `source_start`,
  `source_end`, and `subtitles[]` with real `start`/`end`/`subtitle` per cue.
- Source footage (the speaker video) + its audio.
- Optional: brand/community logo, social handle.

## Workflow

### 1. Verify toolchain before writing any component

```bash
node --version && npm --version      # Node 22+ works; Remotion 4 needs >=18
ffmpeg -version | head -1
ffprobe -version | head -1
```

Reuse an existing Remotion project if one exists under `~/videos/*`
(check `package.json` for `remotion`/`@remotion/cli` and skip `npm install`
entirely). Otherwise:

```bash
mkdir -p ~/videos/<slug>/src && cd ~/videos/<slug>
npm i remotion @remotion/cli react react-dom
npm i -D typescript @types/react @types/react-dom
```

`@remotion/three` + `three` only if the brief actually needs 3D. Most
editorial/kinetic-type work needs neither.

### 2. Extract the design layer from OpenDesign

OpenDesign content lives in `~/videos/open-design` (repo layout):

- `design-systems/<name>/DESIGN.md` — palette roles, type scale, spacing,
  depth rules, do's/don'ts. This is the authority for color and type.
- `design-systems/_schema/` — `manifest.schema.ts`, `tokens.schema.ts` if you
  need to validate a custom system.
- `skills/` — functional skills (editorial, kinetic-type, brand-extract …).
- `plugins/_official/video-templates/` — reference motion treatments
  (`frame-kinetic-type`, `frame-light-leak-cinema`, `frame-vignelli`, …).
  Read the matching one before designing a new transition vocabulary.

Read the chosen `DESIGN.md` and transcribe its tokens into one `theme.ts`
(colors, font stacks, sizes). A brief may override the palette — when it does,
the brief wins, and the override goes into `theme.ts` as a comment.

Fonts: a fresh Linux box usually has **no** Montserrat/Inter/Manrope/Amiri.
Either `npm i @remotion/google-fonts` and `loadFont()` the families, or
install system fonts. Do not silently fall back to DejaVu — check first:

```bash
fc-list : family | grep -iE 'montserrat|inter|manrope|amiri' || echo MISSING
```

### 3. Ingest source footage

```bash
uvx yt-dlp -f 'bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080]' \
  --merge-output-format mp4 -o source.mp4 '<URL>'
```

Then cut only the needed ranges (keeps the render small and makes
`OffthreadVideo` seek cheap):

```bash
ffmpeg -ss 00:05:26 -to 00:06:29 -i source.mp4 -c copy clips/c01.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 clips/c01.mp4
```

Use `@remotion/media`'s `OffthreadVideo` (or `remotion`'s) for playback —
never `<video>` with manual `play()`, it desyncs.

**Datacenter-IP pitfall (costs an hour if unknown):** YouTube returns
`Sign in to confirm you're not a bot` from cloud/VPS IPs. Installing `deno` as
a JS runtime or rotating `player_client` (android/ios/mweb/tv/web_embedded)
does **not** fix it — the flag is on the IP. Public mirrors are also mostly
dead (Invidious `403`, Piped inherits the same block, cobalt v7 API shut down).
Stop after one attempt and ask the user for the `.mp4` or a `cookies.txt`
(`--cookies cookies.txt`); do not burn turns on proxies.

### 4. Composition skeleton

```tsx
// src/index.tsx
registerRoot(() => (
  <Composition id="Clip01" component={Clip01} durationInFrames={1890}
    fps={30} width={1080} height={1920} />
));
```

Derive `durationInFrames` from the clip plan, never hardcode:
`Math.round((source_end - source_start) * fps)`.

Subtitle timing: cue `start`/`end` are absolute video time; inside a clip they
become `cue.start - clipStart` in seconds → frames. Convert once in a
`subtitleAt(frame)` helper, keep the cue text verbatim.

### 5. The three-zone layout

Default for lecture/education clips (1080×1920):

```
┌─────────────────────────────┐  0
│  TOP 5–15%   kicker + rules │
├─────────────────────────────┤
│  PRESENTATION / VISUAL      │  18–72%  full-bleed width, no side padding
│  (the thing being talked    │
│   about: slide, workflow,   │
│   code, diagram)            │
├─────────────────────────────┤
│  ◯ speaker   │  subtitles   │  74–88%  circle inset left, 2–3 lines right
└─────────────────────────────┘  100%
```

- Speaker in a **circle** (or soft-cornered) inset, `objectFit: cover`,
  `objectPosition: center 30%` to keep the head in frame. Never distort.
- Subtitles sit **beside** the speaker inset, not under it: max 2–3 lines,
  34–44 px, `textWrap: balance`, keyword in the accent color.
- Hard rule: **nothing overlaps the face** — no ornament, border, sticker,
  texture or type on the face. If the inset is tight, shrink the circle.
- Keep all text ≥120 px from the bottom edge (platform UI) and ≥80 px from top.

### 6. Motion vocabulary

Stay inside this set; more transitions = more ways to look cheap:

- masked horizontal wipe for headline reveals (clip-path inset, 300–700 ms)
- staggered word entrances, 40–60 ms apart, `spring({damping: 200})` or ease-out
- scale-in 96% → 100% + opacity fade-up
- gold/accent underline that draws (`scaleX` 0→1, left origin)
- slow push-in on the speaker: 100% → 104% over the clip, never more
- one light sweep per clip maximum
- cinematic fade or brief dark frame between clips

Forbid: glitch, spin, flash, bounce, more than one accent animation per beat.

### 7. Verify before the full render

```bash
npx tsc --noEmit
npx remotion compositions src/index.tsx
npx remotion render src/index.tsx Clip01 out/c01-preview.mp4 --frames=0-89 --codec=h264 --crf=24
ffmpeg -y -ss 2 -i out/c01-preview.mp4 -frames:v 1 out/c01-frame.png
```

Inspect the still with `vision_analyze` / `browser_vision`: text inside safe
margins, subtitle not clipped, speaker face uncovered, contrast readable.
Fix, re-render preview, then:

```bash
npx remotion render src/index.tsx Clip01 out/c01.mp4 --codec=h264 --crf=22 --concurrency=2
ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=codec_name,width,height,r_frame_rate,pix_fmt -of json out/c01.mp4
```

Long renders: run as a tracked background process with completion notification,
not a 600 s foreground call.

## Quality gates

- Exact 1080×1920, 30 fps, H.264, duration matches the clip plan ±1 frame.
- Original audio preserved and in sync (verify: spoken word at 1 s matches).
- Every subtitle cue from the plan appears, verbatim, at its timestamp.
- No text outside safe margins; no clipping on 3-line subtitles.
- Palette and type come from `theme.ts` only — no ad-hoc hex in components.
- Each clip differs in composition (hero statement / diagram / code / split)
  while sharing identity.

## Pitfalls

- `interpolate()` with `extrapolateLeft/Right: 'clamp'` everywhere, or text
  flickers back in at the end of a sequence.
- `Sequence` children get local frame 0 — always subtract the clip start.
- `OffthreadVideo` needs a static-able path: put media in `public/` and use
  `staticFile()`, or pass an absolute path from the project root.
- 90 s of 1080×1920 Three.js takes minutes; editorial layouts render in tens
  of seconds. Do not add 3D to a typography brief.
- `tsconfig` needs `"jsx": "react-jsx"`, `"esModuleInterop": true`, and
  `"skipLibCheck": true` (Three/WebCodecs lib collisions).
- Never abbreviate honorifics in subtitles, hooks, kickers or end cards —
  expand them fully on every occurrence.

## Pre-processing real lecture recordings (the part that actually takes time)

A YouTube lecture recording is **not** a clean speaker clip. It is a screen
share with a tiny webcam tile composited in a corner. Two separate assets have
to be cut out of it before Remotion sees anything:

```bash
# 1. the slide/presentation, cropped to just the slide area, scaled to frame width
ffmpeg -i clip.mp4 -vf "crop=960:540:0:90,scale=1080:606:flags=lanczos" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an c01-pres.mp4

# 2. the webcam tile, tight square, green keyed to the theme's background
ffmpeg -f lavfi -i "color=c=0x101827:s=632x356:r=24:d=800" -i clip.mp4 \
  -filter_complex "[1:v]crop=316:178:964:272,scale=632:356:flags=lanczos,\
chromakey=0x03E082:0.32:0.10[fg];[0:v][fg]overlay=shortest=1,format=yuv420p" \
  -c:v libx264 -crf 18 -an c01-face.mp4
```

Hard-won specifics:

- `libx264` rejects odd dimensions. Round crop/scale to even numbers
  (`606` ok, `607` → `height not divisible by 2`).
- `chromakey=0x00ff00` often fails on a graded virtual background: sample the
  actual pixel first (`PIL`/`magick`), then key that hex with `similarity 0.30`
  and `blend 0.08`. Two-pass `colorkey` after `chromakey` only helps if there's
  residual spill.
- Don't scale the webcam beyond ~2× its native size — a 316 px tile becomes
  mush at 632 px. Keep the circular inset small (Ø≈292 px in a 1080 frame) and
  let the layout carry the weight instead.
- Verify the crop with a still **before** rendering: head clipped at the crown,
  a name lower-third bleeding in, or a burned-in channel logo all look like
  composition bugs downstream.
- Where you can't key cleanly, a themed background behind a square-to-round
  `overflow: hidden` inset reads better than a hard green rectangle.

## Audio

Per-clip cut files carry the speech; play them alongside with Remotion's
`Audio` and nothing else:

```tsx
<Audio src={staticFile(`${clip.id}.mp4`)} />
```

Do not re-encode audio to a separate track — re-muxing a clip whose video you
already cropped keeps A/V locked. Check loudness with
`ffmpeg -i out.mp4 -af volumedetect -f null -` (mean ≈ −19 dB is healthy for
speech) rather than trusting the render log.
