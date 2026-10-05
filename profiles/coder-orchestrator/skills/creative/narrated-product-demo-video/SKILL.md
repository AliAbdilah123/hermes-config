---
name: narrated-product-demo-video
description: Produce verified product-flow demo videos with screen recording, concise narration, captions, privacy review, and delivery checks.
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    category: creative
    tags: [video, demo, screencast, voiceover, captions, product]
---

# Narrated Product Demo Video

Use this skill when the user asks for a demo, walkthrough, screencast, or narrated product-flow video.

## Delivery contract

The deliverable is a playable video file, not a proposed shot list. Do not claim that recording or rendering is underway until the recording stack has passed preflight. If direct capture is blocked, state the precise boundary and request the smallest user-supplied input needed (normally an unedited screen recording), then perform the editing, narration, captioning, and verification yourself.

## Workflow

1. **Define the exact flow.** Confirm only decisions that materially alter the recording: environment/URL, start and end states, narration language, required checkpoints, aspect ratio, and whether any transaction must actually complete. Infer ordinary choices.
2. **Preflight before promising production.** Verify browser launch, page reachability, viewport, session/auth availability, recorder output, audio renderer, and final encoder. Record a 3–5 second disposable clip and probe it before beginning the real flow.
3. **Respect sensitive boundaries.** Never type passwords, payment-card data, API keys, OTP/2FA codes, or other secrets. Never approve permission prompts or payment actions without explicit authorization. Use sanctioned test accounts and provider test mode. Pause for user action when a protected step is unavoidable.
4. **Capture cleanly.** Use a stable viewport, suppress unrelated notifications, avoid personal tabs, leave short handles before/after each action, and visibly verify the final state. Prefer one clean take; use cuts only where they improve clarity or remove waits/sensitive content.
5. **Write narration from observed footage.** Describe what is actually visible and why each important step matters. Keep sentences short and action-synchronized. Do not describe a successful payment, redirect, or persistence check unless the footage proves it.
6. **Produce audio and captions.** Generate voiceover, normalize speech, mix it without clipping, and add readable captions. Avoid covering primary controls, prices, status messages, or confirmation details.
7. **Privacy and integrity review.** Inspect frames around login, checkout, redirects, receipts, and account pages. Blur or cut private identifiers. Preserve enough context to prove the demonstrated result.
8. **Verify the artifact.** Probe codecs, duration, resolution, frame rate, and audio stream; play representative start/middle/end segments; confirm narration timing and legibility; then deliver the file with a one-line summary.

## Checkout demos

Show, where applicable: item/package selection → order review → checkout initiation → provider test payment → return redirect → persisted purchase/order verification. A provider page alone is not proof of completion. Use test-mode transactions and record exact result/status identifiers only when safe and requested.

## Capture fallback ladder

1. Preferred browser automation/recording path.
2. An already-installed compatible browser supplied via an explicit executable path.
3. Attach to a deliberately launched browser through CDP and verify control with a disposable page/clip.
4. Native desktop capture when authorized and available.
5. Ask the user for a raw recording, with a precise shot checklist; retain responsibility for narration, captions, editing, and final validation.

Do not repeatedly retry an unverified setup. Move up the ladder only after a concrete probe fails.

## Quality bar

- Default: 1080p or the app's natural desktop viewport, 30 fps, H.264/AAC MP4.
- Speech is intelligible and louder than incidental UI audio.
- Captions match narration and remain within safe margins.
- No dead air, loading waits, secrets, unrelated windows, or unsupported success claims.
- The final frame clearly shows the promised completion state.

## Supporting material

See `references/production-checklist.md` for a compact preflight, capture, narration, and verification checklist.
