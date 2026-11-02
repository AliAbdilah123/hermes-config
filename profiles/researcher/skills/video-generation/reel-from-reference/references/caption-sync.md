# Caption sync: ASR is a timing oracle, not a caption source

The bug this file exists to prevent, observed in production:

1. `script.json` said `"say": "Jangan tiru videonya. Ukur dulu ritmenya."`
2. OmniVoice rendered it faithfully.
3. `timeline` fed that WAV back through Whisper with `word_timestamps=True`
   and built cues from `w.word`.
4. The burned-in caption read **"Jangan tiru vidionya"** — Whisper had
   "corrected" a word it misheard. Perfect timings, wrong copy.

It passed typecheck, rendered clean, and looked correct in a thumbnail. It was
only caught by asking a vision pass to *read the subtitle text exactly*, on a
frame pulled from the final mp4.

## Rule

**Timing from Whisper. Text from `script.json`.** Never the reverse.

Reasons this holds generally, not just for this pipeline:

- The script is ground truth — you wrote it. ASR is a noisy derivative.
- TTS audio is *harder* to transcribe than human speech (unnatural prosody),
  so error rates are higher than the ~5% you'd expect on a podcast.
- Non-Latin scripts, slang, and loanwords are exactly where the user cares most
  and exactly where ASR invents spellings.
- Subtitle text is burned into the frame, so an error is unrecoverable without
  a re-render.

## Algorithm

```python
def wrap_cues(words, text, max_words=4):
    """words: Whisper word objs (.start/.end). text: the authored line."""
    tokens = text.split()
    if not words or not tokens:
        return [{"start": 0.0, "end": 99.0, "text": text}]   # last-resort: whole line

    n, k = len(tokens), len(words) / len(tokens)
    cues = []
    for i in range(0, n, max_words):
        chunk = tokens[i:i + max_words]
        if len(words) == n:                     # counts match: use real boundaries
            start, end = words[i].start, words[i + len(chunk) - 1].end
        else:                                   # dropped/merged words: proportional
            start = words[min(int(i * k), len(words) - 1)].start
            end = words[min(int((i + len(chunk)) * k) - 1, len(words) - 1)].end
        cues.append({"start": start, "end": max(end, start + 0.35),
                     "text": " ".join(chunk)})
    return cues
```

`max(..., start + 0.35)` guarantees a cue is never zero-length, which would make
the subtitle flash for a single frame or vanish entirely.

`max_words=4` keeps a 1080-wide frame to 2–3 lines at 46 px. Bump it only after
looking at a still — wrapping is a visual property, not a text property.

## Self-check (no framework, run inline)

```python
c = wrap_cues(words, "Jangan tiru videonya ukur dulu")
assert all(a["start"] < a["end"] for a in c)                        # no zero cues
assert all(x["end"] <= y["start"] + 1e-6 for x, y in zip(c, c[1:])) # no overlap
assert "vidionya" not in str(c) and "videonya" in str(c)            # script wins
```

The third assert is the regression test for the actual bug. Adapt the pair of
strings to the project's language; the point is that a *known-correct*
spelling survives the round trip.

## Verification that catches it end-to-end

Text-level checks pass even when the wrong code path ran. Verify on pixels:

```bash
ffmpeg -y -loglevel error -ss <cue_time> -i out/<slug>.mp4 \
  -frames:v 1 -update 1 /tmp/chk.png
```

Then have a vision pass **read the subtitle aloud verbatim** — asking "is the
subtitle readable?" will get you a yes, because it is readable, just wrong.
Ask for the exact characters.

## Related

- Whisper `vad_filter=False` here on purpose: a VAD will merge or drop short
  utterances at scene edges and desync the proportional fallback.
- Caption times are scene-relative at first, then offset by `scene.start` once.
  Offsetting twice is the other way this silently drifts.