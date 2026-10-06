# Evolving captured social messages into a searchable note library

Use this reference when inbound Instagram/Facebook messages already become notes and the requested change spans message shaping, external-post loading, tags, filters, export, or bulk deletion.

## Inspect the entire mutation and read path

Before planning, locate:

- every provider ingestion path and webhook fixture;
- manual note create/update paths;
- note schema, DTO, scanner, and list/detail queries;
- provider media-resolution endpoint and detail-page trigger;
- library route, URL-state handling, pagination, and existing delete endpoint.

A derived field such as tags must be refreshed on every create/update path through one shared transactional helper. Avoid an implementation that updates manual edits but not provider inserts, or one provider but not another.

## Message-to-note contract

Specify and test:

- which message text becomes the title;
- title length behavior while retaining full text in the body;
- body ordering when a URL exists (`URL`, newline, message);
- URL provenance (message text, attachment permalink, captured fallback URL);
- avoidance of duplicate URLs already present in the message;
- attachment-only events and split provider deliveries;
- idempotency under duplicate webhook delivery.

Webhook capture should persist original IDs/URLs only. It must not fetch external media during ingestion.

## Quota-safe external enrichment

If provider calls consume quota, merely opening or preloading a note must not resolve the post. Plan an explicit accessible **Load post** action and prove:

1. detail GET/page open performs zero resolution/provider calls;
2. activation makes the request once;
3. cached success remains usable;
4. failure preserves the note and original URL;
5. retry is available on a later activation/open.

An explicit POST/command endpoint is preferable to a resolution GET because browser prefetching and route preload should not create provider traffic.

## Hashtag-derived tags

Define before implementation:

- Unicode versus ASCII hashtag syntax;
- punctuation and word-boundary behavior;
- case-insensitive normalized identity and display casing;
- per-note deduplication;
- stale-link removal when edits remove hashtags;
- whether tags are derived from body, title, or both;
- ANY versus ALL semantics for selecting several tags.

Use normalized `tags` plus a note/tag join table when filtering and reuse matter. Add indexes for normalized tag lookup and note joins. Replace links transactionally with the note write; do not leave tag reanalysis as an asynchronous best-effort job unless scale proves it necessary.

## Library filters and bulk operations

Do not assume “homepage” identifies a route. Check redirects/navigation and state explicitly whether controls belong on the dashboard or notes library.

For filters:

- encode multi-select values as repeated URL parameters;
- combine filter groups with AND and values within a group with documented OR/AND semantics;
- preserve search ranking, pagination totals, URL back/forward restoration, ownership scope, and stale-request protection;
- bound count/length and parameterize SQL.

For selection:

- define “select all” as visible page or all filtered results;
- define what happens after filter/page changes;
- show selected count and destructive confirmation;
- retain/report failed items after partial deletion.

For a modest visible-page batch, reuse the existing owner-scoped CSRF-protected delete endpoint with bounded sequential calls. Add a bulk endpoint only when atomicity or measured scale requires it.

For Markdown export, decide combined file versus per-note/ZIP, deterministic order, metadata/tag format, separators, and filename. Prefer browser-local generation with a fixed safe filename when no server work is needed.

## Acceptance evidence

Require focused tests plus authenticated public E2E. Include network/log evidence that opening detail does not invoke resolution before **Load post**. Build, source changes, and HTTP 200 alone do not prove quota behavior or interaction correctness.
