# Provider webhook media-shape discovery

Use this when text ingestion works but attachment-only webhook events are dropped and the provider's real media payload is not yet proven.

## Safe sequence

1. Correlate the user's send time with privacy-safe service logs and receipt rows. Report exact receipt time, whether processing ran, the result, and whether a record was created.
2. Add, test, build, deploy, restart, and health-check a temporary shape diagnostic **before** asking for another send. A resend before the diagnostic is live yields no new evidence.
3. Log only attachment count, an allowlisted attachment type, and bounded/sorted top-level and payload key names. Never log URLs, titles, message text, raw sender/recipient/page IDs, signatures, tokens, or raw JSON. Hash operational IDs only when correlation is necessary.
4. Ask for one fresh send after deployment and inspect only the new diagnostic line. Never infer payload structure from an older receipt captured before deployment.
5. Implement only observed fields: validate HTTPS URL/host, type, item count, serialized size, recipient/page, and verified sender; preserve order; persist atomically with receipt and destination record; retain replay deduplication.
6. Render native image/video/audio only for proven browser-safe media. Otherwise provide a safe external link. Add proxy/download/object storage only if real URL expiry or authentication behavior requires it.
7. Once redacted fixtures and parser tests cover the shape, remove temporary diagnostics or gate them behind an explicit diagnostic mode.

## Minimum verification

- A privacy test proves secret values and raw identifiers never enter logs.
- Tests cover attachment-only, text-plus-attachment, replay, wrong recipient/page, unknown sender, unsupported type, and malformed attachment.
- Full backend tests pass; deployed service restarts; public health succeeds.
- A fresh live event proves parsing, then authenticated public UI proves ordered media is visible only in the correct user's record.

## Meta subscription distinction

Page `feed`, `video`, and `messaging_postbacks` subscriptions do not prove that content shared inside Messenger arrives in the expected message attachment payload. Verify the relevant messaging subscription separately and treat the signed callback as the contract.
