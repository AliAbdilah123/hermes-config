# Lazy external media cache planning

Use this when webhook-delivered records reference external media that is unnecessary until a user views the record.

## Core boundary

```text
webhook → validate/dedupe → create durable record → store payload-supplied references → acknowledge
```

The webhook must not call the provider merely to enrich or download media. Preserve references already supplied in the event: provider message/media ID, original URL/permalink, type, and payload title when available.

Enrichment is an explicit detail-view command:

```text
detail page genuinely mounts → display local record → explicit resolve command
  → persistent hit: return cache, no provider call
  → miss: bounded provider fetch → atomic cache save → return enrichment
  → failure: retain record/references and return degraded success
```

## Prevent accidental fetches

Do not attach external side effects to a generic read endpoint that route prefetching might call. Prefer:

- `GET /api/items/{id}`: local-only and side-effect-free;
- `POST /api/items/{id}/media/resolve`: authorized command that may contact the provider;
- `GET /api/items/{id}/media/{key}`: ownership-checked cached-byte delivery.

Call resolve only after the actual detail component mounts. Test that webhook receipt, startup, dashboard/list/search, hover, route preload, polling, and cache hits make zero provider calls.

## Persistent state and failure contract

Use the smallest persistent state machine: no row (`not_fetched`), `fetching`, `available`, `failed`.

Store original references separately and never overwrite them with cache fields. Provider/storage failure must not fail, delete, hide, or invalidate the source record. Return it successfully, omit unavailable enrichment, and allow retry on a later genuine detail open. Add a short failure cooldown to avoid refresh storms and a stale-claim timeout to recover interrupted work.

Use an atomic conditional claim/transaction so concurrent detail opens do not duplicate provider traffic. Cache metadata and binary media independently when partial success is useful.

## Safe binary caching

- Authenticate and verify ownership before resolving or serving bytes.
- Accept only validated HTTPS provider URLs and redirects.
- Set strict request timeout, byte ceiling, and content-type allow-list.
- Stream to a generated temporary filename and atomically rename after complete success.
- Never join a client-provided filesystem path or expose local paths.
- Serve using the stored allow-listed type plus `X-Content-Type-Options: nosniff` and a private cache policy.
- Keep tokens, signed URLs, raw provider bodies, and secrets out of logs.
- Cascade cache metadata on source deletion and remove files best-effort without resurrecting a deleted record.

## Acceptance matrix

1. Webhook stores references and performs zero provider calls.
2. List/search/dashboard/preload perform zero resolve/provider calls.
3. First genuine detail open on a miss performs one bounded provider fetch.
4. Second and post-restart opens use persistent cache with zero provider calls.
5. Fetch/download/write failure leaves source content and original link usable.
6. A later post-cooldown detail open retries.
7. Concurrent opens acquire one fetch claim.
8. Cross-user resolve/media reads are denied without revealing existence.
9. Invalid type, redirect, timeout, oversized, and interrupted-write cases publish no partial file.

## Scope discipline

Do not add scheduled refresh, proactive warming, generalized provider frameworks, CDN/object storage, admin cache controls, or background jobs unless requested. If large media later requires asynchronous processing, the job must still originate from a genuine detail-open resolve so unopened records cause no provider traffic.
