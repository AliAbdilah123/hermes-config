# Provider message attachment ingestion

Use when a signed social/messaging webhook may deliver text and media separately.

## Establish the real contract first

1. Add a short-lived capture only **after signature verification**. Gate it behind explicit runtime configuration, write mode `0600` into a mode `0700` directory, and never log raw bodies.
2. Send uniquely marked provider messages covering the requested media classes.
3. Record redacted fixtures preserving nesting, attachment type, provider media ID, URL shape, message IDs, sender/inbox IDs, timestamps, ordering, and split-event timing.
4. Probe media URLs without printing query values: report scheme, host, path, query-key names, status, MIME type, redirects, and browser renderability.
5. Delete raw captures, remove capture instrumentation/runtime overrides, restore the normal binary, and verify health **before** implementation.

## Preserve provider semantics

Do not normalize a provider type such as `ig_post` into a renderer type such as `image`. Store/API descriptors preserve observed semantic fields:

```json
{"type":"ig_post","url":"https://…","media_id":"…"}
```

Map renderer behavior separately: the UI may render an `ig_post` URL in `<img>` only when the observed MIME contract proves it is an image preview. Require all identity/rendering fields; reject incomplete descriptors. Validate allowed type, HTTPS, expected host, item count, and serialized size. Never expose provider tokens. Keep caption/alt metadata separate from note title.

## Correlate split events narrowly

When evidence shows attachment-only first and text second with different message IDs:

- correlate only the observed direction: text may complete a still-empty attachment draft;
- scope by configured inbox plus active verified stable sender;
- enforce the measured short inactivity window;
- record every external message ID in a dedicated dedupe ledger;
- never append attachments to a recent text note;
- never append text to a finalized, manually edited, or non-empty note;
- never use a generic “latest note within N seconds” query;
- persist nothing for unmatched/unverified senders.

A completion query should require same identity, empty content, non-null attachment metadata, creation inside the window, and unchanged-since-creation evidence. Prefer a provider correlation ID if later evidence supplies one.

## Verification

- Fixture parser asserts exact `type`, non-empty `url`, and non-empty `media_id`.
- Store regressions cover attachment → text merge, replay of both IDs, sender/inbox isolation, outside-window separation, unrelated later text, manual-edit protection, and zero unverified persistence.
- API regression asserts exact names and absence of credentials.
- UI renders media between title and content, hides empty media, and reloads persisted data.
- Back up/integrity-check the live DB before migration; test upgrade and clean bootstrap.
- After deployment, send a fresh provider share and text, inspect redacted logs, verify exactly one persisted note/dedupe, then exercise the authenticated public detail page on desktop/mobile.
