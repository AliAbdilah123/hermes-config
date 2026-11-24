# Offline-first implementation — Light POS (session notes)

Concrete decisions and pitfalls from building offline-first into a Vite/React + Node/SQLite POS app. The SKILL.md carries the durable rules; this file holds the specific implementation detail.

## What actually got built

- `src/offline.ts` — native IndexedDB, three object stores:
  - `meta` — cached `{user, tenants, business}` session under key `'session'`
  - `snapshots` — key `${userId}:${business}`, value `{userId, business, revision, data}`
  - `outbox` — keyPath `id`, value the full operation envelope
- `src/serviceWorker.ts` — pure `buildServiceWorker({base, version, assets}) => string`; a Node build script (`scripts/build-service-worker.mjs`) hashes the emitted asset list into `app-shell-build-<sha1>`, writes `dist/sw.js`. A `src/serviceWorker.test.ts` unit-tests the generated string (cache naming, API exclusion).
- `server/app.mjs` — `/api/sync` with a `sync_operations` table (`id`, `actor_id`, `business_id`, `status`, `created_at`, `result_revision`, `result_data`). Schema migration adds `result_data` via `PRAGMA table_info` check.

## The rebase flaw (the key technical lesson)

First implementation had `rebaseOperation(op, newBaseRevision)` — replay mutated the queued op's original `baseRevision` to the latest accepted revision. This **rewrote the revision guard**, so a stale full snapshot could be accepted against a revision it was never based on and overwrite concurrent state. The fix: **never rebase**. Instead `compactOperation` keeps the original `id` + `baseRevision`, replacing only `action`/`data`. Multiple offline edits collapse into one cumulative snapshot per `(userId, business)`.

```ts
export const compactOperation = <T>(operation, data, action, scope = {userId: operation.userId, business: operation.business}): Operation<T> => {
  if (scope.userId !== operation.userId || scope.business !== operation.business) throw Error('Operation scope mismatch.');
  return {...operation, action, data};
};
```

## Sync endpoint semantics (server)

- Per-op validation: `text(id,100)`, `operation.userId === user.id`, `text(createdAt,40)`, `Number.isInteger(baseRevision)`, `text(action,200)`, `canAccess(user, business)`, `validState(data, business)`.
- Idempotency lookup by **global `id` alone**; if found but actor/tenant mismatch → `409`. If found and matches → return stored `status`/`revision`/`result_data` (lost-response recovery).
- `BEGIN IMMEDIATE` → read `app_state` row → `row.revision !== baseRevision` → `ROLLBACK` + `{status:'conflict', revision, data: before}`. Else apply, bump revision, append audit, insert op, `COMMIT`.
- `authorizeMutation` still applies on the candidate so privilege escalation isn't bypassed by the sync path.

## Client sync loop

```
sync():
  revalidate /session owner == outbox owner (else 401/403 → stop, keep outbox)
  for each op (in created order, scoped to user+tenant):
     result = POST /api/sync {operations:[op]}
     if not accepted → mark conflict, break (never overwrite)
     if no result.data (duplicate) → fetch authoritative /api/state
     apply result.data, bump revision, cacheSnapshot, removeOperation
```

Key client-side guards:
- Capture `{userId, business, baseRevision}` synchronously in `update()`.
- `queue.current = queue.current.catch(()=>undefined).then(...)` keeps the chain alive after IndexedDB failure.
- Generation-check `loadState` so out-of-order tenant loads can't apply the wrong tenant's data.
- Reconstruct working state from the latest pending snapshot (`pending.at(-1)?.data`) so a server refresh doesn't silently drop optimistic local edits.
- `keepServer` discards conflicting op(s); with compaction there's only one cumulative op per scope so the "dependent later ops resurrect the change" hazard is structurally avoided.

## Public E2E (proves offline-first, not just unit tests)

Two scripts (Playwright core, `/snap/bin/chromium`):

1. **Shell + session** — login, wait for SW `controller`, assert `activated` + correct scope; `setOffline(true)` + reload → cached auth boots, status "Offline"; `setOffline(false)` + dispatch `online` → "Online".
2. **Offline mutation** — login, navigate to `/notes`, `setOffline(true)`, add a note (tag it uniquely), assert `.sync-status` shows "Pending"; `setOffline(false)`, click "Sync offline changes", reload, assert the tagged note persists.

The tag-id uniqueness (`E2E-offline-<Date.now().toString(36)>`) keeps runs non-colliding against retained server data.

## Deployment gotchas hit

- Cloudflare default `max-age=14400` cached the old `sw.js` (`cf-cache-status: HIT`, `age: 6612`) AFTER the origin was correct. Fixed with nginx `add_header Cache-Control: no-cache, no-store, must-revalidate` on the exact `sw.js` location → forces `BYPASS` without a purge token. `index.html` got `no-cache`, manifest `no-cache`, `/assets/` `public, max-age=31536000, immutable`.
- `rsync -a --delete` left `sw.js` mode `600` → nginx `403`. Diagnosed with `namei -l`; fixed permanently by deploying with `--chmod=Du=rwx,Dgo=rx,Fu=rw,Fgo=r`.

## Verification totals (for reference, not a promise)

133 frontend vitest + 29 backend node:test, typecheck, build, eslint (0 errors) green; both public E2E passed; commit + push to `main`.