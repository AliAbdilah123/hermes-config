---
name: short-form-video-clip-planning
description: Create and validate timestamp-accurate short-form clip plans from supplied SRT transcripts, including creative metadata and file-based JSON delivery. Use for TikTok, Reels, and Shorts clip selection or when preparing structured clip plans for a video-production pipeline.
---

# Short-Form Video Clip Planning

Create clip plans from the supplied transcript only. Preserve cue boundaries and return machine-consumable artifacts.

## Source discipline

1. Treat the attached SRT as the sole source of spoken content and timestamps.
2. Do not infer transcript content from a source URL.
3. If the SRT is absent or unreadable, stop with the exact failure response requested by the user.
4. Parse real cues only. Ignore malformed timestamp records rather than inventing corrected timings.

For the parse → survey → candidate-window → generate recipe (including the
`NaN:NaN:NaN,NaN` and empty-cue junk filters, and a working window enumerator),
see `references/srt-parsing-and-window-selection.md`. Long lectures: sample
every 5 minutes first, never read the transcript linearly, and never hand-write
the subtitle objects — emit them from the parsed cues.

## Clip construction

1. Select self-contained sections with a strong opening and complete ending.
2. Keep every clip within the requested duration range.
3. Include contiguous cues only; never skip an intervening cue.
4. Keep clips non-overlapping and distribute them across the source.
5. One subtitle object equals one original SRT cue.
6. Preserve subtitle text verbatim, except for removing SRT numbering/tags and joining multiline text from the same cue with spaces.
7. Convert timestamps exactly as requested, dropping milliseconds only at final serialization.
8. Set `source_start` from the first included cue and `source_end` from the last included cue.

## Creative fields

Titles, kickers, and hooks may be concise and editorial, but must not add claims absent from the selected passage. If quoting transcript language in a creative field, preserve the quotation exactly.

A `hook` is display copy that becomes a 3-second on-screen headline, not a
transcript excerpt. Prefer a complete stand-alone clause over a verbatim quote
that begins mid-sentence — an SRT cue often opens with the tail of a previous
thought (`"question tuh bagaimana? Jadi eh kita angkat…"`), which reads as a
broken title at 78 px. Only quote verbatim when the cue starts a sentence.

## Validation

Before delivery, programmatically verify:

- every subtitle text and timestamp maps to an actual source cue;
- cue IDs are contiguous inside each clip;
- source bounds match the first and last subtitle cues;
- durations meet the requested range;
- clips do not overlap;
- identifiers and parts are sequential;
- the final artifact parses as valid JSON.

Do not silently weaken these checks to make a chosen segment pass; choose a better segment.

## Delivery preference

For this user, when the requested output is JSON, write it to a descriptive `.json` file and deliver the file attachment directly. Do not paste the JSON body into chat unless the user explicitly requests inline JSON. Keep accompanying prose absent or minimal.

This held for the clip plan **and** for any other JSON deliverable in the same
pipeline (render manifests, scene configs). When the user says "kirim file aja,
jangan message", they mean the artifact itself — reply with the attachment and
at most one line of context, never a fenced JSON block plus an explanation.

## Pitfalls

- A `hook` is on-screen display copy, not just a field. Quoting a fragment that
  starts mid-sentence (e.g. `"question tuh bagaimana? Jadi eh kita angkat…"`)
  reads as a broken title when rendered large. Either quote an utterance that
  begins at the start of a cue, or write a complete stand-alone clause. When the
  clip plan feeds a motion-graphics render, the hook becomes the 3-second
  headline — validate it as a headline, not as a transcript excerpt.
- Do not end a clip on a cue whose text clearly continues into the next cue merely because the duration is valid.
- Do not begin with a sentence fragment solely to improve the hook.

## Downstream: this plan feeds a video render

When the same session continues into production, see
`references/remotion-render-handoff.md` — it covers the seconds-based data module
the composition needs, why `--get` breaks yt-dlp, what to do when the source
footage is blocked or still pending, and the still-frame QA loop that catches
text collisions before the full render.
- Dropping milliseconds can create visible gaps or equal-looking boundaries; validate using original millisecond timestamps, then serialize.
- A creative summary is allowed only in creative fields, never in `subtitles`.
