# Offline-first PWA release verification

Use this checklist when releasing an SPA that caches its shell and queues authenticated mutations.

## Data-safety checks

- Test two or more queued offline mutations. If each carries a full cumulative snapshot, replay them sequentially and rebase each later operation onto the revision returned by the previously accepted operation. Sending the batch with one shared base revision makes every operation after the first conflict.
- Persist an outbox record before treating an optimistic mutation as durable.
- Resolve IndexedDB writes on transaction completion, not request success; a request can succeed before the transaction later aborts.
- Cache the authenticated session after both initial session restoration and a fresh interactive login. Testing only the already-authenticated boot path misses first-login offline failure.
- Fall back to cached authentication only for network/unavailable failures. An explicit HTTP authentication failure must show sign-in rather than resurrect a stale cached session.
- Verify logout purges the current user's cached session, snapshots, and outbox.
- Conflicts remain pending until explicit user resolution; never silently replace either local or server data.

## Service-worker checks

- Honor the app's build base path and deployed scope.
- Never Cache Storage-cache API responses or credentials.
- Verify shell reload while the browser context is actually offline, not merely with `navigator.onLine` mocked.
- Verify the service worker is activated and controls the page before switching offline.
- Check deployed file permissions. `rsync` from a restrictive temporary directory can publish service-worker/manifest files as mode `600`, producing public 403 responses even while `index.html` works. Deploy with explicit readable modes, for example `--chmod=Du=rwx,Dgo=rx,Fu=rw,Fgo=r`.

## Root-mounted domain deployment

A Vite app may build with `/projects/<slug>/` for its internal compatibility route while users access `https://dev-<slug>.example.com/` through an nginx rewrite/sub-filter bridge.

- Inspect nginx's actual alias/root before copying; similarly named `/var/www/...` and `/usr/share/nginx/...` trees can coexist.
- Test the user-facing root-mounted domain, not the retired or guarded `/projects/...` URL.
- Set the public E2E base URL explicitly when the canonical script defaults to an old path.
- Verify app `200`, unauthenticated API's expected status, service worker `200`, manifest `200`, service-worker scope, offline reload, and reconnect.
- If the broad public E2E stops on known fixture-label drift, do not weaken it. Record the drift and run a focused deployed offline/reconnect probe against actual production fixtures.

## Minimum release evidence

1. Frontend tests, backend tests, typecheck, lint, and production build.
2. Service restart and direct backend health/auth check.
3. Public shell, service worker, and manifest fetches.
4. Browser: online sign-in, controlling worker, true offline reload into cached authenticated state, pending mutation persistence, reconnect replay, duplicate replay, and concurrent-revision conflict.
5. Independent final diff review before commit/push.
