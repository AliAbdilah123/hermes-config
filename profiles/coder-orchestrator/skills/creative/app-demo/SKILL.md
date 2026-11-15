---
name: app-demo
description: Use when creating an end-to-end web or app demo video that must show natural cursor movement, visible clicks, human-paced typing, smooth transitions, synchronized voice-over, captions, privacy review, and verified final media.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    category: creative
    tags: [video, demo, browser, recording, narration, captions]
    related_skills: [narrated-product-demo-video, computer-use]
---

# App Demo

## Overview

Produce a finished, playable product-demo video—not a script or collection of screenshots. The recording must look like a deliberate human demonstration: the pointer travels to controls, clicks are perceptible, text appears character-by-character, page changes retain visual continuity, and narration describes only what the footage proves.

Default deliverable: 1080p or the app's natural desktop viewport, 30 FPS, H.264 video, AAC audio, synchronized captions when appropriate, plus verification frames and `ffprobe` evidence.

## When to Use

Use for:

- Product walkthroughs and feature demonstrations.
- Browser or native-app flows with clicks, typing, scrolling, and state changes.
- Login, onboarding, CRUD, checkout test-mode, and error-state demonstrations.
- Re-recording a technically valid demo whose interactions feel abrupt or robotic.

Do not use for a static screenshot, conceptual storyboard, or unsupported claim about an unobserved flow.

## 1. Define the Demonstration Contract

Before recording, determine:

- Exact URL/application and environment.
- Start state, ordered actions, and required final state.
- Target duration and aspect ratio.
- Narration language and tone; default to concise English.
- Whether captions are required; default to included when voice-over is included.
- Any irreversible action, payment, protected login, or secret boundary.

Infer ordinary production choices. Ask only when an unknown materially changes the demonstrated claim or crosses a protected boundary.

**Complete when:** every scene has a visible start state, action, expected result, and narration purpose.

## 2. Preflight the Entire Stack

Verify before promising production:

1. Browser/app launches at the target viewport.
2. The target page is reachable and renders correctly.
3. Automation can move a visible pointer, click, type incrementally, and wait on page state.
4. Recorder creates a playable 3–5 second clip.
5. Voice renderer produces intelligible audio.
6. FFmpeg can encode H.264/AAC and `ffprobe` can inspect the result.
7. Output paths have enough free space.

Prefer a real browser under Xvfb or native display capture when the cursor must be recorded. Playwright's direct page video may omit an OS cursor; if so, render a cursor overlay driven by the same timed pointer trajectory, or capture the displayed browser through FFmpeg. Do not proceed with screenshot stitching when a real interaction recording is possible.

**Complete when:** a disposable clip includes visible pointer motion and playable audio and passes `ffprobe`.

## 3. Build a Human-Paced Interaction Timeline

Use one timeline as the source of truth for automation, recording, narration, and captions.

### Pointer motion

- Move the pointer along an eased path over roughly 350–800 ms for ordinary targets; use longer travel for distant controls.
- End near the control's visual center without teleporting.
- Pause 150–350 ms on hover before clicking so the target is readable.
- Make clicks perceptible with a brief ripple, ring, or pointer compression lasting 120–250 ms when the recorder does not naturally show clicks.
- After clicking, hold long enough to show the pressed/focus state before the next transition.

### Typing

- Focus the field visibly with a click.
- Type character-by-character, typically 45–110 ms per character with small deterministic variation.
- Use slightly longer pauses around punctuation and between fields.
- Never inject the entire value instantly with DOM assignment, `fill()`, pasted text, or JavaScript unless the demo explicitly demonstrates paste.
- Keep passwords and secrets out of footage. For sanctioned fake passwords, masked typing may be shown.

### Scrolling

- Use smooth, bounded scroll segments rather than jumps.
- Stop with the target fully visible and leave 400–900 ms for orientation.
- Avoid unnecessary scrolling that adds motion without meaning.

### State changes

- Wait on a concrete UI condition—URL, visible heading, enabled button, dialog, or error—not a blind delay alone.
- Preserve 500–1200 ms of the prior state before an important action and 1–2 seconds of the resulting state afterward.
- Trim genuine long waits in editing; never fabricate a successful state.

**Complete when:** a dry run visibly shows every click, typed character sequence, transition, and final state without abrupt jumps.

## 4. Capture a Clean Take

- Use a stable viewport and browser zoom.
- Close unrelated tabs and suppress notifications.
- Start recording 1–2 seconds before the first action.
- Keep the pointer parked in a neutral area during narration-only holds.
- Record one clean take when possible; use cuts only to remove waits, sensitive content, or failed attempts.
- Never include real passwords, OTPs, tokens, payment details, or private identifiers.
- For error demos, make one sanctioned invalid submission and stop at the proved error state.

**Complete when:** the raw take contains the entire requested flow and no unrelated or sensitive content.

## 5. Write Voice-over From Observed Footage

Watch the raw take first. Then write narration against actual timestamps.

Rules:

- Narrate the user's intent and observed result, not every cursor movement.
- Use one short idea per sentence.
- Lead actions slightly or speak during natural travel/typing time; do not announce a result before it appears.
- Leave room around important UI sounds or visual states.
- Do not claim success, persistence, payment, or validation unless visible footage proves it.
- For short demos, prefer 2–5 concise sentences and avoid introductions such as “In this video.”

Example for failed login:

1. “From the Komuna homepage, I’ll open the sign-in page.”
2. “I’m entering a clearly invalid test account.”
3. “Komuna rejects the attempt and keeps the user on the sign-in form with a clear error message.”

**Complete when:** every spoken claim maps to a visible time range in the recording.

## 6. Render Audio and Captions

1. Generate voice audio with the configured TTS provider.
2. Normalize speech loudness and prevent clipping.
3. Align sentence starts to the corresponding visible action/result.
4. Add readable captions inside safe margins without covering controls or error messages.
5. Mix incidental UI audio below narration, or omit it when it adds no value.
6. Encode H.264 video plus AAC audio in MP4 unless the destination requires another format.

Default FFmpeg verification expectations:

- Video stream: H.264, `yuv420p`, constant presentation at 30 FPS unless source differs.
- Audio stream: AAC, intelligible speech, no clipping.
- Resolution: target viewport or 1920×1080.

**Complete when:** narration is synchronized, captions match, and primary UI remains unobscured.

## 7. Review Motion, Privacy, and Integrity

Watch—not merely probe—the start, every state transition, and the final state. Extract representative frames and inspect them.

Reject and re-record when:

- The pointer teleports or clicks are not visible.
- Text appears all at once when typing is meant to be demonstrated.
- Navigation cuts before the viewer can understand the prior state.
- Narration describes a result before it appears or after it disappears.
- A cursor obscures the final message.
- Browser chrome, development hostnames, test data, or placeholder content make the artifact unsuitable for its intended audience.
- Any secret or private identifier appears.

Technical checks:

```bash
ffprobe -v error \
  -show_entries format=duration,size \
  -show_entries stream=codec_name,width,height,avg_frame_rate,pix_fmt \
  -of json output.mp4
ffmpeg -v error -i output.mp4 -f null -
```

Also confirm the audio stream exists and listen to the complete narration.

**Complete when:** the video passes full decode, visual review, audio review, privacy review, and the requested flow is unmistakable.

## 8. Deliver

Provide:

- The playable video file.
- One sentence describing the demonstrated outcome.
- Brief verified media facts: duration, dimensions, video/audio codecs.
- Any honest audience-facing caveat, such as use of a development environment.

Do not present intermediate scripts, raw recordings, or extracted frames as the final deliverable unless requested.

## Codex Delegation Prompt Requirements

When delegating production to Codex or another CLI agent, explicitly require execution and artifacts. Include:

- “Execute the flow; do not merely write a script.”
- Exact output paths.
- Visible eased cursor movement and click indicators.
- Character-by-character typing with timing bounds; forbid instant `fill()`/DOM value injection.
- Concrete waits on UI state.
- A disposable preflight clip.
- Voice-over generated only after observing the raw footage.
- AAC audio and synchronized captions.
- Start/middle/end frame extraction, `ffprobe`, full decode, and visual/audio review.

After delegation, independently verify the artifact. An agent's success report is not proof.

## Common Pitfalls

1. **Screenshot slideshow disguised as a demo:** record continuous interaction instead.
2. **Headless browser with no pointer:** capture a displayed browser or render a synchronized pointer/click overlay.
3. **Instant Playwright `fill()`:** use incremental keyboard input with per-character delay.
4. **Blind sleeps:** wait for visible state, then add only a presentation hold.
5. **Narration authored before capture:** write it from observed footage so claims and timing remain accurate.
6. **Technical-only verification:** a valid MP4 can still feel robotic; watch the transitions and interactions.
7. **Voice-over without captions:** include captions by default unless the user opts out or the destination makes them inappropriate.
8. **Sensitive demo data:** use obvious fictional data and inspect login/checkout frames closely.

## Verification Checklist

- [ ] Exact flow and audience are defined.
- [ ] Disposable clip proves browser, pointer, click, recorder, TTS, and encoder.
- [ ] Pointer moves smoothly; no teleporting.
- [ ] Clicks are visible.
- [ ] Typing is character-by-character and human-paced.
- [ ] Important states have readable holds.
- [ ] Voice-over matches observed activity and timing.
- [ ] Captions are accurate and do not cover key UI.
- [ ] No secrets or private data appear.
- [ ] H.264 video and AAC audio streams are present.
- [ ] Full decode succeeds.
- [ ] Start, transitions, and final state were watched.
- [ ] Final artifact—not a plan—is delivered.
