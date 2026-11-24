---
name: offline-first-data-sync
description: "Implement and repair offline-first data synchronization: durable outbox, idempotent replay, conflict retention, session-owner validation, and build-versioned service-worker caching, without silently losing or overwriting server state."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [offline, sync, idempotency, outbox, service-worker, indexeddb, pwa]
    related_skills: [code-change-verification, test-driven-development, feature-pos-operations]
---

# Offline-First Data Sync

Use when adding or fixing offline capability: an ordered durable mutation outbox, revision-guarded/idempotent replay against an authoritative server, conflict retention, session-owner validation before replay, and predictable service-worker shell caching. Native browser APIs only (IndexedDB + Cache Storage) unless a dependency is already present.

## Core invariants

1. **Never rebase an immutable queued snapshot.** Changing a persisted operation's `baseRevision` lets a stale full snapshot look current and overwrite state committed after it. For multiple offline edits, compact them into ONE latest cumulative snapshot per user+tenant, preserving the original `baseRevision` and the stable operation ID. A conflict stops replay and stays pending/visible.
2. **Idempotency keys on the global ID alone.** Server uniqueness must look up by operation `id` inside the write transaction; a scope mismatch (different actor/tenant reusing the ID) returns 409, never a missed-row + 500. Persist the accepted result snapshot so a duplicate replay of a committed-but-lost-response op can return the authoritative server-normalized data. When a duplicate *may* already have landed, fetch authoritative `/api/state` before removing/reconciling the outbox entry.
3. **Capture scope synchronously.** Read `{user, business, baseRevision}` in `update()` before the promise queue runs, and use those immutable values through enqueue/send/cache. Tenant switch or logout mid-queue must not tag one tenant's snapshot as another's.
4. **Generation-check every async result.** Loads and syncs can resolve out of order; drop any result whose captured user+tenant no longer matches current refs. Keep pending/conflict state per tenant.
5. **Never let a refresh clobber optimistic work.** Reconstruct working state from the latest pending snapshot (`pending.at(-1)?.data ?? serverData`) so a reload/tenant-load doesn't silently discard in-flight edits.
6. **Recoverable queue + honest durability.** Chain as `queue = queue.catch(()=>undefined).then(...)` so one IndexedDB rejection can't strand later writes. Persist outbox + snapshot in a single IndexedDB transaction; report non-durable writes explicitly.
7. **Validate session owner before replay.** Hit `/api/session` first; on 401/403 stop replay, keep pending ops, and require login — never submit or delete another cached user's outbox.

## Service-worker shell caching

Inject a build-derived cache version (content hash of the built asset list, not a hand-typed `-v1`), precache the built shell assets, and on activate delete only prior *app* caches (prefix match) so old hashed assets don't accumulate and mixed versions aren't served. Never cache API responses. Generate the precache list by parsing the built `index.html` asset URLs — regexes must tolerate absolute `/projects/<app>/assets/...` paths, not just root-relative `/assets/...`.

## Online-only surface gating

Centralize a single `online` flag; mark online-only nav/actions (admin, uploads/OCR, printing, tenant/user admin) with an `onlineOnly` marker and disable+label them offline rather than letting each fail ambiguously.

## Pitfalls

- Reading `userId`/`business`/`revision` inside the queued callback instead of at enqueue time causes cross-tenant tagging.
- Global `revision`/`pendingCount`/`conflicts` shared across tenants leak state and let `keepServer` discard another tenant's conflict.
- Duplicate replay returning only `{status, revision}` strands the client: it can't restore the server-normalized data/audit after a lost response + reload.
- `validState`/authorization can reject a "no-op" sync payload as "No changes supplied" — tests that reuse the server's own unchanged data to exercise idempotency must make a real mutation first.
- A service worker with a fixed cache name survives every deploy; old assets accumulate with no update strategy.

## Verification

Frontend: compaction preserves stable ID + original revision; compaction rejected across users/tenants; outbox survives IndexedDB abort; reload recovery. Backend: duplicate replay returns accepted snapshot; cross-scope ID reuse → 409; ordered multi-op replay; stale base → conflict retained. Plus a service-worker source test asserting versioned cache name, precache list, prefix-only activation cleanup, and API exemption. Run the frontend suite and the backend test script separately — backend node tests are not under vitest.

## Support files

- `references/light-pos-compaction-and-idempotency.md` — concrete TypeScript + Node patterns and test recipes from the Light POS offline-first fix.