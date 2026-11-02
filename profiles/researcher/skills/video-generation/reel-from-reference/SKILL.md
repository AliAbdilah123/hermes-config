---
name: reel-from-reference
description: Build an original short-form video (TikTok/Reels/Shorts) by using an existing video as a structural reference rather than a template — yt-dlp to fetch, Whisper to measure pacing, OmniVoice to generate a fresh voiceover, Remotion to render, and ffmpeg to add sound effects in sync. Includes a local web UI to repeat the whole pipeline on the next video. Use when asked to "buat video serupa", remake/adapt a reference video, or set up a repeatable reference-to-reel production pipeline.
---

# Reel from Reference

Turn one reference video into an unlimited series of **original** videos, then
repeat it from a browser instead of retyping commands.

Working language for this user: **casual Indonesian** (`lo/gue` register) in
chat and in the UI's labels; the reel's own `headline`/`body` copy should be
Indonesian, short, and uppercase-friendly. Report results in Indonesian — and
report what actually ran (durations, file paths, measured dB), not what was
supposed to run.

The rule that makes this legitimate and reusable:

> **The reference is measured, never imitated.** Extract *numbers* from it
> (words/second, pause length, segment length, hook duration, scene count) and
> write a completely new script, voice, and visual set against those numbers.
> Copying the script, the voice, the edit, or the thumbnails is a different,
> worse task — and it produces a video that competes with its own source.

## Pipeline

```
ingest → transcribe → tts → timeline → render → mix → out/<slug>.mp4
 yt-dlp   Whisper     OmniVoice  word-align  Remotion  ffmpeg+SFX
```

Every stage writes one JSON artifact to `work/`, so any stage can be re-run
alone without redoing the expensive ones:

| Stage | Reads | Writes |
|---|---|---|
| `ingest` | URL or file | `work/source.mp4`, `work/ref.wav` |
| `transcribe` | `ref.wav` | `work/ref.json` (pacing stats + transcript) |
| `tts` | `script.json` | `work/say/<id>.wav` per scene, `work/say.json` |
| `timeline` | `say.json` + `script.json` | `work/timeline.json` (absolute cue times) |
| `render` | `timeline.json` | `out/video.mp4` (silent) |
| `mix` | `timeline.json` + `public/sfx` | `out/<slug>.mp4` (final) |

`script.json` is the only hand-authored file. Everything else is derived, which
is exactly what makes the next video cheap: new `script.json` → run 4 stages.

## Environment

```bash
# one-time: OmniVoice is CPU-only here (no GPU, 11 GB RAM) — slow but works
uv venv ~/.venvs/omnivoice --python 3.11
uv pip install --python ~/.venvs/omnivoice/bin/python \
   --index-url https://download.pytorch.org/whl/cpu torch torchaudio
uv pip install --python ~/.venvs/omnivoice/bin/python omnivoice faster-whisper
export HF_HOME=~/.cache/hf-omnivoice     # keep the 3.2 GB model off the default cache

# Remotion: reuse an existing shared install rather than re-downloading 400 MB
ls ~/videos/node_modules/remotion || npm i remotion @remotion/cli react react-dom
```

`omnivoice` pulls `transformers>=5.3` and needs a recent `torch`; if `pip`
resolves an old torch you get `AudioTokenizer` import errors, not a clear
version message. Pin torch from the CPU index **first**.

Measured cost on 2 CPU cores, no GPU:

- model load ≈ 56 s (once per `tts` invocation — batch all scenes in one call)
- `num_step=16` → RTF ≈ 17; `num_step=8` → RTF ≈ 8.7 (2–4 min for a 20 s reel)
- Whisper `small` int8 ≈ 0.3× realtime; `tiny` for iterating on timings

Never run `tts` in a 600 s foreground call. Use a tracked background process
with completion notification, or the UI (which already does this).

## CLI

```bash
SK=~/.hermes/profiles/researcher/skills/video-generation/reel-from-reference
PY=~/.venvs/omnivoice/bin/python

$PY $SK/scripts/reel.py init       ~/videos/my-reel
$PY $SK/scripts/reel.py ingest     ~/videos/my-reel "https://youtube.com/watch?v=..."
$PY $SK/scripts/reel.py transcribe ~/videos/my-reel model=small
$PY $SK/scripts/reel.py tts        ~/videos/my-reel          # ← background it
$PY $SK/scripts/reel.py timeline   ~/videos/my-reel
$PY $SK/scripts/reel.py render     ~/videos/my-reel
$PY $SK/scripts/reel.py mix        ~/videos/my-reel
```

Override the interpreter and model per call: `REEL_PY=/path/python`,
`REEL_WHISPER=small`.

### Design the script from the measurements

`work/ref.json` gives you `words_per_sec`, `mean_segment`, `mean_pause`,
`suggested_scene`. Use them as **targets**, then write new copy:

```json
{"title": "…", "lang": "id",
 "theme": {"bg": "#0B0F14", "fg": "#F4F1EA", "dim": "#8A93A0",
           "accent": "#FFB300", "accent2": "#4ADE80", "font": "Inter"},
 "voice": {"model": "k2-fsa/OmniVoice", "instruct": "male, low pitch",
           "speed": 1.0, "steps": 8, "clone": ""},
 "scenes": [{"id": "s1", "kind": "hook", "kicker": "…",
             "headline": "…", "body": "…", "say": "kalimat yang diucapkan"}]}
```

Scene `kind` drives both layout and SFX: `hook` (loudest type + riser/hit),
`point`, `stat` (giant number), `list`, `end` (sub boom). 5 scenes ≈ 20–25 s;
keep hooks ≤ 3 s spoken.

`voice.instruct` is OmniVoice *voice design* (gender, age, pitch, accent,
`whisper`). `voice.clone` is a path to a 3–10 s WAV for voice cloning — only
with the speaker's explicit permission. OmniVoice also accepts inline tags like
`[laughter]` and `[sigh]` in `say`.

## Sync model (the part people get wrong)

Durations are **derived from the generated audio**, never planned in advance:

1. `tts` speaks each scene → `work/say/<id>.wav`
2. `timeline` measures each WAV and lays scenes back-to-back (`start`, `dur`)
3. Remotion's composition length = `timeline.duration`
4. Captions: **Whisper supplies timing only; the words come from `say`.** Re-transcribing
   TTS output silently corrupts your own copy (measured: `videonya` → `vidionya`).
   Cut cues from `script.scenes[].say.split()`, map them onto the Whisper word
   timings, offset by the scene's `start`. If the token counts disagree (Whisper
   dropped or merged a word) slice proportionally instead of showing wrong text.
   See `references/caption-sync.md`.
5. `mix` delays each narration by `start`, adds SFX at scene-relative offsets,
   then `apad,atrim` to the exact timeline length

Consequence: never hardcode `durationInFrames`. It is
`round(timeline.duration * fps)` and changes every time you edit a line.

## Audio

Narration is the bed; SFX are sparse accents — one per beat, never a bed of
noise. `scripts/sfx.py` synthesises everything procedurally with ffmpeg (no
asset downloads, no licence questions):

```bash
$PY scripts/sfx.py public/sfx whoosh hit riser click sub
```

| name | use |
|---|---|
| `riser` | tension into the hook / a reveal |
| `hit` | landing the hook, a hard cut |
| `whoosh` | scene transition |
| `click` | text or number arrival |
| `sub` | low boom on the end card |
| `tick` | counting / data texture |

Final loudness for social: `loudnorm=I=-14:TP=-1.5:LRA=11` then
`alimiter=limit=0.95`. Verify, don't assume:

```bash
ffmpeg -i out/<slug>.mp4 -af volumedetect -f null -
# healthy: mean ≈ -17 dB, max ≈ -1 dB
```

## Custom UI (repeat on the next video)

```bash
REEL_PY=~/.venvs/omnivoice/bin/python \
  ~/.venvs/omnivoice/bin/python -m uvicorn \
  --app-dir <skill>/ui app:app --host 127.0.0.1 --port 8770
```

One HTML page, no build step. What it does:

- lists projects under `REEL_ROOT` (default `~/videos`) with stage badges
- creates a new project (`init`) from a slug
- ingests a reference by **URL or file upload** (`yt-dlp` path is the same code)
- shows the measured pacing stats so you write against facts
- edits `script.json` per scene (say / headline / body / kicker / kind / voice)
- runs any subset of stages, streams the log, auto-chains the rest
- previews and downloads the final mp4

The UI shells out to `scripts/reel.py` for every action. It never
reimplements a stage, so CLI and UI can't drift.

### Verify the UI without rendering it in a browser

Screenshots are slow and flaky; the API contract is what actually breaks.
Exercise every endpoint the page's JS calls, including the failure paths:

```bash
B=http://127.0.0.1:8770
curl -s $B/api/projects                                  # list renders
curl -s -X POST -F "slug=ui smoke test" $B/api/projects   # slug is normalised
curl -s $B/api/job/<id> | python3 -m json.tool           # poll the job
curl -s -X PUT -H 'content-type: application/json' \
     -d @script.json $B/api/script/<slug>                # script roundtrip
curl -s -X PUT -H 'content-type: application/json' \
     -d '{"scenes":[]}' $B/api/script/<slug>             # MUST 4xx, not 200
curl -s -X POST -F "stages=timeline,render,mix" $B/api/run/<slug>
curl -s $B/api/result/<slug>                             # final file + url
```

Then one full run through those endpoints only — that is the real test that
"the UI can repeat the process", which is the actual requirement. Assert the
produced mp4 with `scripts/verify.py` rather than eyeballing the log.

A 500 on a validation path is a bug, not a pass: the editor sends whatever the
user typed, so `scenes: []` and a scene missing `kind` must both be rejected
with a readable `detail`.

## Quality gates

Run the mechanical gate first — it is one command and it catches the errors that
log-reading misses (truncated tail, 96 kHz audio, wrong duration):

```bash
$PY scripts/verify.py ~/videos/my-reel
```

It asserts 1080×1920 / 30 fps / H.264 / 48 kHz stereo AAC, duration equal to
`timeline.duration` within one frame, audio not truncated, mean volume in
[-20, -14] dB, peak ≤ -0.5 dBTP, and monotonic cue timings inside their scenes.
Exit code 1 on any failure. Then the manual checks:

```bash
npx tsc --noEmit
ffprobe -v error -show_entries format=duration \
  -show_entries stream=codec_name,width,height,r_frame_rate -of json out/<slug>.mp4
```

- 1080×1920, 30 fps, H.264 + 48 kHz stereo AAC
- final duration == `timeline.duration` (±1 frame); if audio is short, you forgot `apad`
- loudness ≈ −14 LUFS integrated, peak ≤ −1 dBTP
- every `say` line's caption appears at its spoken time **and reads exactly as
  written in `script.json`** (grep the rendered timeline for the script's own
  spelling — a Whisper-derived cue will drift a vowel and you won't notice in a
  thumbnail)
- headline inside safe margins; subtitle block clears the platform UI
  (keep ≥ 250 px from the bottom edge — TikTok/Reels controls live there)
- progress bar reflects **global** position (`scene.start + t) / duration`, not
  per-scene progress reset
- always inspect a still from the *final* mp4, not just a Remotion still:
  ```bash
  ffmpeg -y -ss 10.5 -i out/<slug>.mp4 -frames:v 1 -update 1 out/chk.png
  ```

## Pitfalls (each one cost real time)

- **`registerRoot()` is mandatory** in the entry file. Remotion refuses to
  bundle an entry that only exports components.
- **`loadFont()` must run at module scope**, and the entry must import
  something from that module. A bare `import "./fonts"` side-effect import still
  let the bundle tree-shake the call → `delayRender()` timeout after 28 s with
  a stack trace that names none of your code.
- **`--props` needs an absolute path.** A relative path is resolved against the
  CLI cwd, and the error message ("neither valid JSON nor a file path") is
  misleading — the file does exist, just not where Remotion looked.
- **Mix paths must be absolute too.** Passing relative inputs to `ffmpeg` with
  `cwd=<project>` produces `<project>/<project>/work/...` and
  `Error opening output: No such file or directory`.
- **`amix` truncates to the last sample**, so `atrim` alone can't reach the
  timeline length and `-shortest` clips the tail. `apad` before `atrim`.
- **`loudnorm` outputs 192 kHz.** Resample back with `aresample=48000` or the
  muxed AAC reports `sample_rate 96000`.
- **`aeval`/`volume` expressions with `t` need `eval=frame`** in ffmpeg ≥ 6;
  expressions like `lowpass=f='300+6000*(t/1.1)'` are invalid (the filter's
  `f` is evaluated once) — use static filters plus a volume envelope.
- **uvicorn needs `app:app` lowercase**; a module exposing only `APP` fails with
  `Attribute "app" not found`.
- **yt-dlp from a datacenter IP**: YouTube returns *"Sign in to confirm you're
  not a bot"*. That flag is on the IP — `player_client` rotation, a JS runtime
  (deno), and public mirrors (Invidious/Piped/cobalt) do not fix it. Pass
  `--cookies cookies.txt` or upload the file. Budget one attempt, then fall back.
- **Odd pixel dimensions** break `libx264`; round crops/scales to even numbers.
- **`tsc --noEmit` passing means nothing about runtime.** It happily compiled a
  composition whose fonts never loaded and whose entry lacked `registerRoot`.
  Always follow a clean typecheck with `npx remotion compositions` — that is the
  first command that actually evaluates the bundle.
- **Never let ASR text reach the screen.** Whisper transcribing your own TTS is
  a timing oracle, not a caption source; use its word boundaries and your
  script's words.
- **Check the *final* mp4, not the Remotion still.** The Remotion still was
  perfect while the muxed file had 96 kHz audio and a clipped tail.
- **Odd pixel dimensions** break `libx264`; round crops/scales to even numbers.
- Fresh Linux box has no Inter/Montserrat — always `loadFont()`, never rely on
  system fonts, and don't load 6 weights (each is a network request per render).

## Files

```
scripts/reel.py        all stages, one CLI, idempotent per stage
scripts/sfx.py         procedural SFX via ffmpeg lavfi (no downloads)
scripts/verify.py      exit-1 gate: dimensions, codecs, duration, loudness, cues
templates/remotion/    index.tsx, Reel.tsx, types.ts, fonts.ts, tsconfig, package.json
templates/script.json  starting point for a new video's script
ui/app.py              FastAPI: projects, ingest, script CRUD, stage runner, media
ui/index.html          single-page UI, no build step
references/            deeper notes, load only when you hit the matching problem
```

- `references/data-contract.md` — exact schema of `script.json`,
  `ref.json`, `say.json`, `timeline.json`, and which files are safe to hand-edit.
- `references/omnivoice-tts.md` — modes (design / clone / auto), generation
  params, measured CPU timings, voice-consent rules.
- `references/remotion-cli-invariants.md` — the CLI errors with their real
  causes and fixes (entry point, fonts, `--props`, duration).
- `references/caption-sync.md` — why ASR text must never reach the screen, the
  timing-only merge algorithm, its inline asserts, and the pixel-level check
  that actually catches a mis-transcribed caption.
