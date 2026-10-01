# Social webhook attachment contract capture

Use this when a social-provider webhook is text-only today and attachment support depends on undocumented or variable live payloads.

## Safe discovery sequence

1. Keep signature verification ahead of capture. Never inspect or persist an unsigned request body.
2. Start with the least-invasive diagnostic that can prove the contract. For a simple attachment shape, log only attachment count, an allowlisted type label, and bounded/sorted JSON **key names** at the attachment and payload levels. Unknown or malformed types become `unknown`; never log values, URLs, titles, message text, raw IDs, signatures, tokens, or raw payloads.
3. Use short-lived raw capture only when key-shape diagnostics cannot answer ordering, correlation, or media-capability questions. Gate it by environment and store outside the repository in a dedicated `0700` directory with `0600` files.
4. Test the diagnostic for both expected structure and secret absence, deploy the exact diagnostic binary, verify restart and health, and only then ask the verified sender to resend. Check event timestamps against the deployment timestamp; a callback received before deployment cannot provide the new evidence and requires another resend.
5. Compare callback timestamps, hashed sender/recipient/message identifiers, attachment nesting/type vocabulary, correlation fields, item order, and whether text/media arrive together or separately.
6. Probe media URLs without printing them: report scheme/host/path, query-key names, redirects, status, MIME type, and expiry/auth behavior. Check query keys for signatures or tokens before deciding what may reach the browser.
7. Preserve only minimal redacted fixtures. Replace account IDs, message IDs, media IDs, captions, URLs, signatures, and personal content while retaining exact JSON structure and timing relationships.
8. Remove diagnostic code after parser regressions lock the observed contract, deploy the normal implementation, restart, and verify health. Previously ignored events normally cannot be reconstructed because their attachment metadata was deliberately not stored; request one fresh provider event after the implementation is live.

## Contract-driven implementation rules

- Implement only fields and media types proven by captures; do not fabricate carousel slides from one provider preview image.
- An attachment-only callback followed shortly by a text callback with a different message ID proves split delivery. If product semantics require one note/item, use an explicit pending collection keyed by configured inbox + verified stable sender, finalized after the specified inactivity interval. Do not approximate this by updating or selecting any recent finalized note: that creates a sliding window, can merge unrelated messages, and can overwrite manually edited content.
- Define restart semantics before choosing in-memory timers versus persisted pending groups. Persist enough state when replay dedupe and crash recovery must survive process restart.
- Preserve every external message ID in a dedicated ledger, including IDs absorbed into a grouped item. Test replay of each constituent ID both before and after finalization.
- Perform inbox and stable-sender authorization before retaining attachment metadata, event-ledger rows, or pending-group content. Unverified senders must leave no durable content in any table.
- Keep verification-code messages activation-only even if they unexpectedly include media.
- Treat provider CDN previews and canonical external destinations separately. A signed preview URL is not automatically a safe permanent external link. Expose a minimal descriptor and validate scheme plus the observed provider host; never return raw callback objects or credentials.
- Store ordered descriptors as nullable JSON when attachments have no independent lifecycle. Decode `NULL` to an empty API array, preserve order, and test detail and list scans so schema additions cannot silently break either query.
- Generate default localized titles only in the initial insert from one authoritative creation instant. Tests must prove later text/attachment collection and ordinary edits do not regenerate the title.
- Use exact observed vocabulary in fixtures and parser tests. Unsupported types should fail closed without weakening signature, echo, recipient, sender, or message-ID checks.
- Preserve provider-semantic `type` in storage/API; do not normalize `ig_post` to `image`. Normalize type-specific identifiers (for example `ig_post_media_id` or `reel_video_id`) to the application field `media_id`, while the renderer separately chooses image, video, or embed behavior.
- For split delivery, narrow collection to the proven direction and unfinished shape (for example, text completing a still-empty attachment note within 10 seconds). A query for any recent note by sender is unsafe even when sender/inbox-scoped because it can mutate finalized or manually edited notes.
- Determine media capability from the URL response, not its field name. A Reel callback URL may be an Instagram HTML permalink rather than video bytes. Probe the correct Graph host with the server-side token while redacting secrets. If authorized resolution cannot return a browser-safe media URL, use the official provider embed plus an external-link fallback; never pass an HTML page URL to `<video>`.
- A parent preview URL and media ID do not prove carousel-child access. Add swipeable ordered children only when the callback or an authorized Graph expansion returns all children; never fabricate slides.

### Observed Meta naming examples

- Shared post: `type=ig_post`, payload keys `ig_post_media_id`, `url`, `title`.
- Reel: `type=ig_reel`, payload keys `reel_video_id`, `url`, `title`.
- Normalize both to `{type, url, media_id}` while preserving `type` exactly.

## Focused regression matrix

At minimum cover: observed fixture parsing; attachment-only then text with separate IDs; reversed arrival when observed; same key inside the inactivity window; different inbox/sender isolation; boundary just outside the window; replay of every ID; unverified sender leaves every relevant table unchanged; generated timezone title remains stable; nullable JSON becomes `[]`; descriptor order; unsupported media omission; and rendered title → media → content order with meaningful image alt text and narrow-viewport containment. Run the focused backend regression first, then full backend tests, frontend tests/check/build, and finish with a directly recognized canonical test command so workspace verification evidence is fresh rather than merely human-readable.

## Evidence boundaries

- A text-only note after sharing media is not ambiguous if logs show the media callback was ignored before the text callback; report that exact routing boundary.
- URL/MIME probes establish transport compatibility, not longevity. Re-probe during public E2E.
- Source tests are not provider E2E. Final readiness still requires a fresh live callback, authenticated rendered detail, persistence/reload, replay dedupe, unverified-sender rejection, credential-leak checks, and database cleanup/integrity checks.
