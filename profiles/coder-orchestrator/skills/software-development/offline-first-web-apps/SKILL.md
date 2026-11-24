---
name: offline-first-web-apps
description: Implement offline-first capability in a web app — native IndexedDB session/tenant caching + durable ordered mutation outbox, revision-guarded idempotent sync, and a build-versioned PWA shell (service worker + manifest). Use when the user asks to make an app work offline, add offline mode / offline sync / PWA / installable support, or "cache and replay" writes.
---

# Offline-First Web Apps

Add offline capability with the smallest correct mechanism. Two moving parts: (1) client durability (IndexedDB) plus a PWA shell, and (2) a server sync contract that can never silently lose concurrent edits. Prefer native browser APIs and stdlib — no new dependencies.

## Ladder (use the first rung that holds)

1. **Read-only offline first**: cache the authenticated session + last tenant snapshot + app shell; boot offline for a previously-authenticated user. No outbox yet — this is most of the value at a fraction of the risk.
2. Add a **durable ordered mutation outbox** only when offline *writes* are actually required. The outbox + revision-guarded replay is the expensive, dangerous half.
3. **Service worker**: cache the app shell and immutable hashed assets; NEVER cache `/api/*`. Key caches by a build-derived version so stale shells don't linger.

## Non-negotiable safety rules (data-loss guards — never simplify these)

- **Never rebase a queued snapshot's base revision.** Rebasing rewrites the revision guard and can make a stale full snapshot look current, overwriting state committed since it was captured. Compaction (below) MUST preserve the ORIGINAL `baseRevision` and a stable operation `id`.
- **A conflict stays pending, never silently overwrites.** When the server revision moved past the op's base, return `conflict`; surface it; let the user explicitly discard ("keep server version"). Discarding must also remove/neutralize any dependent later ops so the discarded change can't reapply later.
- **Idempotency keyed globally on the operation id**, not `(actor, tenant)`. A reused id under another actor/tenant must be rejected (409), not silently miss and fail the insert with a 500.
- **Revalidate session ownership before replay.** A cached CSRF/session can outlive the server session; verify `/session` user id matches the outbox owner; on 401/403 stop replay WITHOUT deleting the outbox.

## IndexedDB outbox (native, no deps)

- Stores: `meta` (cached session + tenants), `snapshots` (key `userId:business`), `outbox` (keyPath `id`).
- Multiple offline edits for one user+tenant **compact into ONE cumulative snapshot** — keep the first op's `id` and original `baseRevision`, replace only `action`/`data`. Throw on user/tenant scope mismatch (never compact across scopes).
- Persist outbox + snapshot in **one transaction** (`persistLatest`) so a quota/transaction failure can't strand a non-durable optimistic state; surface "not durable" to the user when persistence fails.
- Capture `{userId, business, baseRevision}` **synchronously** at call time, not inside the async queue — tenant switch / logout between capture and send otherwise tags one tenant's snapshot as another.

## Server sync endpoint shape

- `POST /api/sync` `{ operations: [...] }` → per-op `{status: accepted|conflict, revision, data}`. Enforce CSRF, bounded op count, per-op validation against the authenticated user + tenant access + `baseRevision` integer + `action` length.
- Accepted ops persist `result_data`; a **duplicate replay returns the stored authoritative snapshot** (lost-response recovery), not just `{status, revision}`.
- Apply inside `BEGIN IMMEDIATE`; on revision mismatch `ROLLBACK` + `conflict`; on success bump revision, append the audit entry, insert the op row, `COMMIT`.

## Service worker + manifest

- Generate SW **at build time** with a content-hash cache name (`app-shell-build-<sha1>`) precaching the emitted asset list; on activate, delete only prior `app-shell-*` caches, then `clients.claim()`.
- Base-path-safe: derive scope from `self.location` and the deploy prefix; skip `/api/`; `navigate` requests fall back to the cached shell when offline.
- Register once from `main.tsx` using `import.meta.env.BASE_URL`.

## Verification (must be public E2E — offline-first claims are easily faked)

Prove the whole loop against the real deployment, not just unit tests:
1. Login online → assert SW is `activated` and `.sync-status` reads "Online".
2. `context.setOffline(true)` + reload → assert the cached session boots and status flips to "Offline".
3. Offline mutation → assert "Pending"/"Conflict" status.
4. `setOffline(false)` + trigger sync → assert the change persists after reload and matches the server.

## Pitfalls

- Cloudflare/nginx default-caches `sw.js`/`index.html` (`max-age=14400`), leaving clients on a stale shell after origin updates. Emit `no-store` for `sw.js`, `no-cache` for `index.html`/manifest, `immutable` for `/assets/`; verify origin vs public separately. See `nginx-server-admin` skill.
- `rsync -a --delete` preserves restrictive source modes → nginx 403 on static files. Deploy with `--chmod=Du=rwx,Dgo=rx,Fu=rw,Fgo=r`.
- The cached session/tenant snapshot needs a validity boundary. Purge on logout; don't reopen a revoked/expired user's data from cache forever.
- Service-worker cache writes should be `event.waitUntil(...)` so navigation/asset responses are durably cached before the worker can be terminated.

## References

- `references/offline-first-implementation.md` — concrete decisions, the rebase-flaw → compaction fix, the sync SQLite schema, and the public E2E scripts from the Light POS offline-first build.