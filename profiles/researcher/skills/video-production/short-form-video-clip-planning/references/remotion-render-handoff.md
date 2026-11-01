# Handoff: clip plan → Remotion render

The clip plan is stage one of an SRT → clip plan → vertical video pipeline. These
are the facts from the render side that constrain how the plan should be shaped,
plus the environment gotchas that cost time on the first run.

## What the render stage consumes

- `durationInFrames = Math.round((source_end - source_start) * fps)` — derive it,
  never hardcode. A plan whose `source_end` is a rounded-down `MM:SS` loses up to
  a second of the last cue's tail; that is acceptable for the plan but means the
  render must read the *cue* timestamps, not the clip bounds, for subtitle timing.
- Cue `start`/`end` are absolute video time. Inside a clip they become
  `cue.start - clipStart`. Emit a seconds-based data module alongside the
  `MM:SS` JSON so the composition does not re-parse strings per frame:

```python
# generate src/data.ts from the clip-plan JSON
cues = ',\n'.join(
    '    {start: %.3f, end: %.3f, text: %s}' % (sec(s['start']), sec(s['end']), json.dumps(s['subtitle']))
    for s in clip['subtitles'])
```

- `hook` becomes the 3-second headline at 60–84 px. This is the reason a hook
  must be a complete clause: a verbatim fragment lifted from mid-sentence looks
  like a rendering bug once it is 78 px tall. Plan hooks as headlines.
- `kicker` becomes the small uppercase label in the top zone; keep it 2–3 words.

## Environment

- Reuse an existing Remotion install rather than a second copy:
  `ln -sfn ~/videos/node_modules node_modules` inside `~/videos/<slug>`.
  Because the parent hoists, `@types/react`, `@types/react-dom` and `typescript`
  must be installed in **`~/videos`**, not the child — otherwise `npx tsc --noEmit`
  emits `TS7016: Could not find a declaration file for module 'react'` plus a wall
  of `TS7031` implicit-any errors that all vanish once the types land one level up.
  `remotion compositions` bundles fine even while types are broken, so `tsc` is
  the real gate.
- `@remotion/google-fonts` and `@remotion/media` are separate packages from
  `remotion`; install them explicitly for `loadFont()` / `@remotion/media`'s
  `OffthreadVideo`.
- A fresh Linux box has no Montserrat/Inter/Manrope/Amiri:
  `fc-list : family | grep -iE 'montserrat|inter|manrope|amiri' || echo MISSING`.

## Getting the source footage

```bash
uvx yt-dlp -f 'bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080]' \
  --merge-output-format mp4 -o source.mp4 '<URL>'
```

- `--get` is ambiguous and aborts with `error: ambiguous option`; use
  `--get-title` / `--get-id`.
- Cloud/VPS IPs get `Sign in to confirm you're not a bot` on every
  `player_client` (android, ios, mweb, tv, tv_simply, web_creator, web_embedded,
  android_vr, web_safari). Adding `deno` as a JS runtime does not change it — the
  flag is on the IP, not the tool. Ask the user for the `.mp4` or a `cookies.txt`
  (`--cookies cookies.txt`) instead of cycling mirrors.
- The SRT is still authoritative for text and timings even when the video is
  unavailable, so a clip plan can be delivered before the footage exists.

## When footage is pending

Do not stall the design work waiting for the file. Render against a stand-in with
a burned-in timecode, review the geometry, then swap the file at the same path:

```bash
ffmpeg -y -f lavfi -i "color=c=0x101827:s=720x1280:r=30:d=400" \
  -vf "drawtext=text='SOURCE FOOTAGE PENDING':fontcolor=0xE4CB86:fontsize=34:x=(w-text_w)/2:y=h*0.28,drawtext=text='%{pts\:hms}':fontcolor=white:fontsize=28:x=(w-text_w)/2:y=h*0.34" \
  -c:v libx264 -preset veryfast -crf 30 -pix_fmt yuv420p public/source.mp4
```

Keep the filename `public/source.mp4` so the composition needs no change.

## Layout the render expects (1080×1920)

```
top 5–15%     kicker + rule + part counter + handle
18–72%        presentation / visual, full-bleed width
74–88%        ◯ speaker circle left  |  subtitles right
```

- Speaker circle `objectPosition: center 28–30%` keeps the head in frame; never
  distort, never put any ornament or type on the face.
- Subtitles beside the inset: cap width ~880 px so the Reels/TikTok action rail
  (right ~120 px) does not cover line ends.
- Anything below y ≈ 1800 will sit under platform UI.

## QA loop that caught real defects

Render 90–150 frames, extract stills at 1 s and 4 s, inspect with a vision pass,
and fix before the full render. Defects it actually caught: hook text colliding
with ghosted background texture, subtitle line ends under the action rail, and a
diagram whose border was too low-contrast to survive H.264. Give the hook an
opaque backdrop rather than dimming the stage — `opacity: 0.92` on a solid fill
still lets texture read through.
