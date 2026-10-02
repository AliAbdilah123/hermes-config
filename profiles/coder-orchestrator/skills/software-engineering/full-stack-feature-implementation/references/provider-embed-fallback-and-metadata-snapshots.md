# Provider embed fallback and metadata snapshots

Use when social/provider content embedded in a saved record later renders “unavailable,” even though the original link may still work for a signed-in user.

## Root cause boundary

An official iframe/oEmbed is not durable storage. It can fail for private or audience-restricted content, deleted content, short/share URLs the embed service cannot resolve, provider policy changes, token expiry, or public-embed restrictions. Do not interpret the provider’s iframe error as proof that the local record disappeared.

## Smallest reliable product pattern

1. Preserve the canonical/original provider URL.
2. At ingestion, capture metadata already present in the signed webhook payload before making another API call.
3. Store only bounded metadata in the existing attachment JSON when possible: type, canonical URL, title/caption, author, thumbnail URL, capture/lookup status, and timestamp. Keep fields optional for backward compatibility.
4. Never put image/video binaries in the relational database. Add object storage only when durable media snapshots are an explicit requirement.
5. If required metadata is absent, permit at most one bounded provider lookup during ingestion. Never perform oEmbed/Graph lookups on every note/detail-page load.
6. Render a native accessible link card from stored metadata. If metadata is unavailable, show an honest “Preview unavailable — open on provider” state.
7. Keep the original external link with `target="_blank"` and `rel="noopener noreferrer"`.
8. Do not render an iframe for the unavailable/fallback state; otherwise the provider’s misleading error becomes the app’s primary UI.

## TDD and verification

- RED backend test: webhook attachment metadata survives parsing, JSON persistence, and note API serialization; metadata-absent attachments receive an explicit fallback status.
- RED frontend test: native card/title/fallback copy is present and provider iframe/plugin URL is absent.
- Verify legacy JSON with only `type` and `url` still unmarshals and renders.
- Run backend tests, frontend tests, type/Svelte checks, and the production-base build.
- Authenticated public E2E must open a real data-backed detail route and assert: native card present, external link present, iframe count zero, console errors zero.
- Create a uniquely named fixture, register cleanup before browser execution, delete child rows explicitly when database foreign keys do not cascade, and assert zero fixture rows remain.

## Pitfalls

- Live oEmbed on every page view adds latency, rate-limit exposure, and another provider outage boundary without solving privacy restrictions.
- Fetching arbitrary thumbnail URLs creates SSRF and content-proxy concerns; use provider-supplied trusted URLs and validation or defer thumbnails.
- Updating exact serialized-JSON assertions is required when adding non-omitempty status fields; distinguish contract updates from production regressions.
- Source/build success does not prove the public authenticated detail route. Verify the exact deployed asset and interaction.
