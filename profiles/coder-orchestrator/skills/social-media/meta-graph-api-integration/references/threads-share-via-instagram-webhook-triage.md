# Threads shares delivered through Instagram messaging

Use when a Threads post sent with Threads’ **Instagram message** action reaches an Instagram webhook but no note/domain record is created.

## Diagnostic signature

A callback may be valid and contain one event while ending with:

- `processed=0`
- `ignored=1`
- `missing_text=1`

This does not prove that Meta sent an empty event. It can mean the event is attachment-only and the attachment failed the application's supported-attachment filter. Distinguish:

1. transport/signature acceptance;
2. event decoding;
3. attachment recognition and URL/media-ID validation;
4. verified-sender/domain processing;
5. persistence and replay handling.

If processing never ran, investigate parsing before routing, ownership, or storage.

## Evidence-first sequence

1. Inspect the newest callback's terminal summary and correlate the narrow journal window.
2. Read the current attachment decoder and allowlist. Check whether native Instagram post/reel payloads are already supported.
3. Check whether the store already accepts attachment-only records and deduplicates external message IDs. If so, avoid schema and frontend work until parsing evidence requires it.
4. Add signature-gated, privacy-safe diagnostics only for attachment-bearing events that would otherwise become `missing_text`.
5. Capture one fresh provider-originated Threads share and preserve its shape as a sanitized fixture.
6. If the callback contains no attachment object, stop and revise the hypothesis; do not invent fields.
7. Add a failing parser-contract test and a signed-webhook persistence/replay test before extending the parser.
8. Add only the observed fields and one narrow normalization branch. Require HTTPS and an explicit observed provider-host allowlist; never accept arbitrary attachment URLs.
9. Verify native Instagram text/post/reel behavior, invalid signatures, wrong recipients, unverified senders, and duplicate delivery.
10. Deploy the exact systemd binary and complete acceptance with another real Threads share plus authenticated public E2E.

## Privacy-safe attachment diagnostics

Safe fields:

- attachment count and index;
- sanitized attachment type;
- sanitized payload key names;
- presence booleans for URL and known media-ID fields;
- URL parse result and scheme;
- coarse/allowlisted host label.

Never log:

- raw webhook payload;
- message text, title, or caption;
- raw URL or query string;
- signature, token, or secret;
- raw sender, recipient, message, entry, or media IDs.

Tests should assert both required diagnostic markers and absence of every seeded private value.

## Minimal implementation boundary

Prefer reusing the existing attachment DTO, persistence transaction, sender verification, and external-message replay ledger. A provider-specific parser branch is usually enough when those layers already work. Do not add a migration, downloader, generic link parser, or frontend redesign without evidence.

Persist provider fields when supplied (`type`, `url`, `media_id`, alt/title). If the product needs display text and the provider supplied none, use a neutral UI/title fallback such as `Shared Threads post`; do not fabricate message body content.

## Acceptance evidence

Report:

- callback timestamp and timezone;
- hashed IDs unless exact-ID logging was separately authorized;
- whether domain processing ran;
- matched/unmatched/ignored reason;
- note insertion versus duplicate;
- authenticated public visibility of exactly one note.

Tests and HTTP health are not substitutes for the final provider-originated callback and public application check.
