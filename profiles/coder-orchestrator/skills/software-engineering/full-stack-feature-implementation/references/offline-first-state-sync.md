# Offline-first state synchronization

Use this reference when adding offline operation to an authenticated, multi-user web application whose current persistence sends whole-state snapshots.

## First decision: distinguish shell availability from write safety

A service worker makes the application load offline; it does **not** make mutations safe. Inspect the complete read/write path before proposing caching:

1. How is the authenticated session restored?
2. What is cached, and under which user + tenant key?
3. Are writes records, deltas, commands, or complete snapshots?
4. Does the server enforce revisions, idempotency, authorization, and tenant scope?
5. What happens when another terminal writes before reconnect?

Never replay a stale whole-state snapshot as though it were a merge. It can overwrite unrelated sales or operational changes.

## Safe staged V1

When the existing application uses revision-guarded whole-state PUTs, the smallest safe first release is:

- Cache the app shell with Cache Storage.
- Store authenticated tenant snapshots and an ordered outbox in IndexedDB.
- Namespace every local record by user ID and tenant ID; purge it on logout.
- Persist an outbox entry before claiming an optimistic change is durable.
- Give each operation a stable idempotency key.
- Apply unseen operations transactionally on the server.
- Accept a queued snapshot only when its base revision still matches.
- Return and retain conflicts for explicit resolution; never silently overwrite or drop them.

This supports a single offline writer safely and **detects** multi-terminal conflicts. Mark this ceiling explicitly. Add domain-specific merges only after real conflict frequency justifies them—for example append-only orders, inventory deltas, or table-state transitions.

## Cache boundaries

- Cache immutable hashed assets cache-first.
- Handle navigation network-first with cached shell fallback.
- Keep API responses and credentials out of Cache Storage.
- Make service-worker scope and URLs respect the application's deployment base path.
- Version caches and test the update path to prevent mixed old/new assets.

## Honest UX

Expose effective states such as Online, Offline, Syncing, Pending N, and Conflict. Do not rely only on `navigator.onLine`; successful and failed requests are stronger signals. Offer manual retry. Clearly disable online-only workflows—login, administration, uploads, remote OCR, network printing, password changes—rather than letting them fail ambiguously.

## Required tests

Write failing tests first for:

- local persistence across reload;
- user/tenant isolation and logout purge;
- ordered replay;
- duplicate replay idempotency;
- stale-base conflict without data loss;
- authorization and tenant-scope rejection;
- offline shell reload;
- queued mutation surviving reload;
- reconnect synchronization;
- second-terminal conflict;
- service-worker scope and cache upgrade.

Public browser verification should exercise online bootstrap, simulated network loss, offline reload/mutation, reconnect, duplicate delivery, and concurrent-terminal conflict at desktop and mobile widths.
