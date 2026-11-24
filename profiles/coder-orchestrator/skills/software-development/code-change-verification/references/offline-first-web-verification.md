# Offline-first web verification

Use this checklist for IndexedDB outboxes, cached authenticated boot, service workers, and conflict-aware synchronization.

## Contract and persistence

- Test operation envelopes, deterministic ordering, user/tenant isolation, and stable IDs independently of browser storage.
- Test real IndexedDB behavior in a browser-capable environment: session/snapshot persistence, outbox survival across reload, migration/open failures, and logout purge for only the current user.
- A DOM test runner may not provide `indexedDB`. Preserve the existing online path when storage is unavailable, but do not treat that fallback as proof that IndexedDB works.
- Persist an operation before reporting an optimistic mutation as durable. Storage failure must remain observable in production; test-only compatibility must not silently weaken this guarantee.

## Server synchronization

- RED/GREEN-test authentication, CSRF, tenant/user isolation, operation validation, ordered application, duplicate replay, and stale-revision conflict behavior.
- Store accepted operation IDs and their result revision transactionally with the state update. Duplicate IDs must return the stored result without reapplying the mutation.
- Conflicts must retain the local operation and return authoritative server data; never silently replace either side.

## Service worker and base path

- Build first, then inspect or exercise the generated output under the actual non-root base path.
- Verify registration URL, scope, manifest `start_url`/`scope`, navigation fallback, and update/cache-version behavior.
- Assert API requests bypass Cache Storage, including APIs mounted below the deployment base path.
- Verify the complete built shell is available offline. Caching only `index.html` on install is insufficient unless every required hashed asset is fetched and cached before going offline.

## End-to-end acceptance

Run a real-browser sequence, not only unit tests:

1. Sign in online and cache a tenant.
2. Disable network and hard-reload.
3. Mutate state offline and reload again; pending state must survive.
4. Reconnect and verify one application plus harmless duplicate replay.
5. Create a second-writer revision conflict; verify visible conflict UI and no overwrite.
6. Resolve by keeping server state, with explicit confirmation.
7. Log out and verify that user’s cached session, snapshots, and outbox are gone.
8. Confirm online-only controls are disabled or clearly labeled offline.
9. Check desktop and narrow viewport, console errors, service-worker scope, and API cache absence.

## Reporting discipline

Report each acceptance check as passed, failed, or not run. Do not summarize a green unit/build suite as full offline-first verification when real IndexedDB or service-worker E2E was not exercised. Include exact commands and outputs, and distinguish pre-existing warnings from new ones.
