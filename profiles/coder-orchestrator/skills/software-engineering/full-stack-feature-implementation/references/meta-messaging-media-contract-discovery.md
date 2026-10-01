# Meta messaging media contract discovery

Use when a signed Meta/Instagram messaging webhook must import shared posts, Reels, videos, or carousels.

## Evidence-first workflow

1. Keep normal logs privacy-safe: receipt/result counters plus hashed sender, recipient, and message IDs. Never permanently log message text, captions, media URLs, signatures, or tokens.
2. If the contract is unknown, temporarily capture raw bodies **only after HMAC verification**. Gate capture by environment variable; use a private directory (`0700`) and files (`0600`).
3. Request uniquely identified examples for every required class: post/image, Reel/video, photo carousel, mixed carousel, and any follow-up text expected to belong to the share.
4. Report only redacted structure: attachment type, payload keys, field lengths, event timing, and `mid` behavior. Preserve redacted fixtures, delete raw captures, remove capture instrumentation/drop-ins, restore the normal binary, and verify health before implementation.

## Preserve provider semantics

Normalize key placement, not meaning:

```json
{"type":"ig_post","url":"https://…","media_id":"…"}
```

Observed provider types can use different identity keys:

- post/share: `type=ig_post`, `payload.ig_post_media_id`;
- Reel: `type=ig_reel`, `payload.reel_video_id`.

Map either identity to public `media_id` while preserving original `type`. The renderer chooses `<img>` or `<video controls>`; storage/API must not rewrite `ig_post` to `image` or `ig_reel` to `video` unless explicitly required.

Require a type-specific media ID and validated HTTPS URL. Bound item count, strings, and JSON size. Never expose provider credentials.

## Split-event collection

Meta can send a share attachment and reply text as separate events with different `mid` values less than a second apart. Never append to any recent note. Require:

- same configured inbox and active verified sender;
- observed direction (attachment-only first, text-only second);
- short evidence-backed window;
- note still empty and unedited/unfinalized;
- every external ID retained for replay dedupe;
- no pending metadata for unmatched senders.

Later attachments or unrelated text create separate notes.

## Carousel expansion

A callback preview plus parent `media_id` does not prove access to carousel children. First determine whether children occur in the callback. If absent, test the supported Graph endpoint server-side with the effective credential. Verify permissions, order, media types, URL expiry/auth, and MIME types. Store only proven ordered children. If expansion is unavailable, show the available preview/link; never fabricate slides.

## Verification

- Fixture/parser tests assert exact `type`, `url`, and `media_id` for each observed type.
- Store tests cover replay, sender/inbox authorization, split timing/direction, manual-edit protection, and unrelated-message separation.
- API tests prove no credential leakage and stable empty arrays.
- Public browser E2E uses fresh real provider messages and verifies playable video or every resolved carousel item, order, swipe/controls, reload persistence, and one-note semantics.
- A privacy-safe `missing_text` log proves only that an attachment was unrecognized; it cannot recover raw provider fields retroactively.
