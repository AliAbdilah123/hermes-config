# Production checklist

## Preflight

- [ ] Exact URL/environment and flow checkpoints identified
- [ ] Test account/session is available without handling secrets
- [ ] Payment or irreversible actions are explicitly authorized and in test mode
- [ ] Browser launches and page renders at target viewport
- [ ] 3–5 second test recording is playable
- [ ] Voice renderer and encoder are available
- [ ] Output directory has sufficient space

## Capture

- [ ] Notifications and unrelated tabs/windows are absent
- [ ] Cursor/actions are deliberate and readable
- [ ] Each major state remains visible long enough to understand
- [ ] Redirects and loading waits are trimmed, not fabricated
- [ ] Final persisted state is reopened or refreshed when persistence is part of the claim

## Narration

- [ ] Script follows observed footage rather than anticipated behavior
- [ ] One idea per sentence; plain language; no filler
- [ ] Important choices, totals, and status changes are explained
- [ ] No claim exceeds what the recording visibly proves

## Privacy

- [ ] Passwords, OTPs, tokens, card data, email/phone/address, and private IDs are absent or redacted
- [ ] Receipts and provider pages are checked frame-by-frame around transitions
- [ ] Test-only data is recognizable without exposing credentials

## Final verification

- [ ] MP4 opens and seeks correctly
- [ ] H.264 video and AAC audio streams are present
- [ ] Resolution, frame rate, duration, and file size are appropriate
- [ ] Voice is clear, synchronized, and not clipped
- [ ] Captions are accurate and do not obscure controls/status
- [ ] Start, middle, and final completion segments were watched
