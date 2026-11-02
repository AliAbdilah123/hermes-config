# Data contract

Four JSON files, one per stage. Only `script.json` is authored by hand; the
other three are generated and must never be edited manually (re-run the stage
instead — hand-edited timings drift from the audio and the whole point of the
pipeline is lost).

## `script.json` — authored

```json
{
  "title": "Jangan Copy, Curi Strukturnya",
  "lang": "id",
  "theme": { "bg": "#0B0F14", "fg": "#F4F1EA", "dim": "#8A93A0",
             "accent": "#FFB300", "accent2": "#4ADE80", "font": "Inter" },
  "voice": {
    "model": "k2-fsa/OmniVoice",
    "instruct": "male, low pitch",
    "speed": 1.05,
    "steps": 16,
    "clone": ""
  },
  "scenes": [
    { "id": "s1", "kind": "hook", "kicker": "STOP COPYING",
      "headline": "Video viral bukan template", "body": "",
      "say": "Berhenti copy video viral. Yang kamu butuh cuma strukturnya." }
  ]
}
```

- `voice.clone` empty → voice **design** via `instruct` (no reference audio).
  Non-empty → voice **cloning** from that wav; consent required.
- `scene.kind` drives both layout and SFX: `hook | point | stat | list | end`.
- `headline` is display text (uppercase, short, ≤ 5 words). `say` is the
  spoken sentence — the two are deliberately different lengths; `headline`
  must not be a transcript of `say`.
- `speed` > 1.0 tightens pacing; check the rendered `ref.json`-style words/s
  after `tts` if it drifts from the reference's measured rate.

## `work/ref.json` — measured reference

```json
{
  "language": "id", "duration": 62.4, "words": 116, "words_per_sec": 1.86,
  "mean_segment": 4.8, "mean_pause": 0.42, "suggested_scene": 4.8,
  "transcript": [ { "start": 0.0, "end": 4.2, "text": "...",
                    "words": [ { "t": 0.0, "w": " Berhenti" } ] } ]
}
```

`suggested_scene` = clamp(duration / segments, 2.0, 6.0) — the target length
of one scene in the *new* video. `words_per_sec` is the pacing budget: match
it, don't exceed it. This file is input to *your* writing, not to Remotion.

## `work/say.json` — generated narration

```json
[ { "id": "s1", "file": "work/say/s1.wav", "duration": 3.62 } ]
```

Paths are **project-relative**. `timeline` resolves them against the project
root; `mix` runs with `cwd=project`.

## `work/timeline.json` — the render contract

```json
{
  "slug": "jangan-copy-curi-strukturnya",
  "title": "...", "fps": 30, "width": 1080, "height": 1920,
  "duration": 22.52,
  "theme": { "...": "copied from script.json" },
  "scenes": [
    { "id": "s1", "kind": "hook", "kicker": "STOP COPYING",
      "headline": "Video viral bukan template", "body": "", "say": "...",
      "audio": "work/say/s1.wav",
      "start": 0.0, "dur": 3.9, "fadeIn": 0.22, "pad": 0.28,
      "cues": [ { "start": 0.0, "end": 1.34, "text": "Berhenti kopi video viral." } ] }
  ]
}
```

Invariants:

- `start` is absolute seconds, scenes are contiguous, `duration` equals the
  last `start + dur`.
- `dur = measured wav duration + pad`. Never authored.
- `cues[].start/end` are absolute (already offset by scene start). Inside a
  `<Sequence>` the local frame is `t - scene.start`, so the comparison in the
  component is `frame / fps + scene.start ∈ [cue.start, cue.end]`.
- `theme` must be present in full; the component never falls back to a
  hard-coded hex.