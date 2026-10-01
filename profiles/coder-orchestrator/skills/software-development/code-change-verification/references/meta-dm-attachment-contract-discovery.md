# Meta DM attachment contract discovery

Use when a signed Instagram/Meta messaging webhook receives shared posts, Reels, or carousels and the provider contract is not yet proven.

## Evidence-first workflow

1. Keep normal webhook logs privacy-safe: receipt/result counts, hashed IDs, and ignore reasons only.
2. Add temporary opt-in capture **after signature verification**, controlled by an environment variable. Write to a private directory (`0700`) with files `0600`; never log bodies, URLs, captions, tokens, or raw IDs.
3. Deploy and verify health before asking the user to resend. Events sent before capture cannot be reconstructed from redacted journals.
4. Request separate examples: post/image, Reel/video, carousel, and text-follow-up. Record timing and whether related parts have distinct `mid` values.
5. Inspect only redacted structure: type, payload keys, lengths, URL host/content type, correlation fields, and timing.
6. Create minimal redacted fixtures preserving shape, then delete raw captures and remove capture instrumentation/service overrides before implementation.
7. Write failing parser/storage/UI tests from fixtures; do not infer unobserved media types or carousel children.

## Contract normalization

Attachment types may use different ID keys:

- Shared post: `type=ig_post`; payload `ig_post_media_id`, `url`, `title`.
- Reel: `type=ig_reel`; payload `reel_video_id`, `url`, `title`.

Normalize application/API descriptors as:

```json
{"type":"ig_post|ig_reel","url":"https://…","media_id":"…"}
```

Preserve provider type; never rename `ig_post` to `image`. Rendering can treat its URL as an image preview while transport/storage remains provider-semantic. Require non-empty type-specific ID, HTTPS, and an allowlisted host. Caption metadata must not replace the generated note title.

## Split-event collection

Meta can send attachment-only and text callbacks less than a second apart with different message IDs. When live evidence proves this:

- dedupe every external message ID;
- scope by configured inbox and active verified sender;
- merge only the observed direction (for example text completing a still-empty attachment note within 10 seconds);
- never query/append to any generic recent sender note;
- never modify finalized, non-empty, or manually edited notes;
- unmatched senders persist no note, attachment, or event metadata.

## Video and carousel boundaries

Probe callback URLs by content type. A Reel URL may be an Instagram HTML permalink, not video bytes. Probe the correct Graph host with the server token while printing only status/error metadata and booleans.

- Browser-safe media URL available: use native media.
- Graph resolution denied/unsupported: use official provider embed plus `Open on Instagram`; never pass an HTML permalink to `<video>`.
- One preview plus media ID does not prove carousel children exist. Add swipeable children only when callback or authorized Graph expansion returns all children in order. Never fabricate slides.

## Verification and cleanup

- Focused RED→GREEN fixture tests per observed type.
- Store tests assert exact `type`, `url`, `media_id`, replay behavior, isolation, timing, and finalized-note immutability.
- UI tests assert Title → media → content and renderer fallback.
- Run full backend/frontend gates, correctly prefixed production build, DB backup/integrity, exact binary/static deployment, local/public health, and a fresh live provider event.
- Remove raw captures, capture directory, service override, and diagnostic binary before completion.
- Do not commit/push or claim READY until the new live event is persisted and visibly rendered through the authenticated public app.
