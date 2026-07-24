# Vite stale-chunk reload root-cause investigation

Use this when SocialZen appears to crash or reload after an authenticated action and a `vite:preloadError` handler exists. Do not assume the handler is the root cause: it is usually the final recovery step.

## Read-only investigation

1. Reproduce while authenticated in production and instrument before the page loads:
   - `beforeunload` / `unload`
   - `vite:preloadError` including `event.payload`
   - `error` and `unhandledrejection`
   - `window.location.reload()` call trace
   - CDP `Runtime.consoleAPICalled`, `Runtime.exceptionThrown`, `Network.responseReceived`, `Network.loadingFailed`, and `Page.frameNavigated`
2. Capture the action request and every request immediately before navigation. Record URL, status, content type, response size, initiator, and requested chunk filename.
3. Rule out independently:
   - React exception / Error Boundary
   - router navigation
   - session invalidation or 401
   - mutation/query rejection
   - explicit reload paths
4. Correlate browser evidence with nginx access logs. A missing hashed `.js` file may appear as HTTP 200 because SPA `try_files` returned `index.html`; status alone is not evidence that the chunk loaded.
5. Compare the requested hashed chunk with files currently under `/var/www/html/projects/socialzen/assets/`. Also compare the request immediately after reload: an old hash followed by the current hash is strong evidence of a stale module graph.

## Confirmed failure chain

A cached old HTML/entry module references an old lazy chunk. Deployment with `rsync --delete` removes that hashed file while browser/Cloudflare caching retains the old module graph. Nginx routes the missing `.js` request to SPA `index.html` and returns HTTP 200 with `text/html` and a suspiciously small body. The browser rejects it as a module/preload failure, Vite emits `vite:preloadError`, and SocialZen's handler calls `window.location.reload()`. The reload fetches the current module graph and current chunk.

The exact reload stack is therefore:

`dynamic import / modulepreload` → unavailable old hash → HTML fallback rejected as JS → `vite:preloadError` → `apps/frontend/src/main.tsx` listener → `window.location.reload()`.

## Evidence standard

Do not call this root cause confirmed from source inspection alone. Require all of:

- authenticated reproduction or matching authenticated production log sequence;
- old requested hash absent from the deployed asset directory;
- response is HTML/fallback or otherwise invalid JavaScript despite a misleading 200;
- current hash loads after reload;
- no competing React, router, auth, Error Boundary, or mutation evidence.

A currently successful action does not disprove the intermittent bug; preserve the successful run as negative evidence and use historical access-log correlation for the stale-client event.

## Safe remediation direction

Do not simply remove the preload handler. Treat it as recovery and fix cache/deployment coherence:

- return a real 404 for missing `/assets/*.js` and `.css`, never SPA HTML;
- serve `index.html` with revalidation/no-cache semantics;
- serve content-hashed assets as immutable;
- publish new assets before switching `index.html`;
- retain previous hashed assets for at least the HTML/CDN cache window instead of deleting them immediately;
- make the preload recovery reload at most once, then show a recoverable update/error UI to avoid loops.

Before changing nginx, inspect repository ownership. If nginx is live-only and no tracked config exists, add a project-owned deploy snippet and report the manual integration step; do not edit live nginx without explicit authorization.

### Smallest safe frontend guard

Use a `sessionStorage` marker and a tiny pure helper typed against `Pick<Storage, "getItem" | "setItem">`. The first preload failure sets the marker and reloads; subsequent failures in the same tab call `preventDefault()`, log the payload, and stop. Do not clear the marker automatically during startup, because clearing before another failed import recreates the loop. Add a focused regression asserting `true` then `false` against one storage object.

### Project-owned nginx contract

Encode three policies separately:

- `/projects/socialzen/assets/`: direct alias/static handling, no SPA fallback; absent files naturally return 404; `Cache-Control: public, max-age=31536000, immutable`.
- exact `index.html`: `Cache-Control: no-cache`.
- SPA navigation routes: fallback to `index.html` with `no-cache`.

Validate the snippet with an isolated minimal nginx config. For unprivileged syntax checks, set `access_log off` so `nginx -t` does not fail merely because it cannot open the system access log.

### Deployment and verification

Do not use `rsync --delete` for routine publication while stale HTML can exist. Sync additively so old hashes survive at least the HTML/CDN cache window; prune later under an explicit retention policy. Publish assets before `index.html`, purge/revalidate CDN entries that already cached HTML under asset URLs, and verify after authorized deployment:

1. nonexistent asset returns 404 and not `text/html`;
2. current hashed JS/CSS has the correct content type and immutable caching;
3. `index.html` revalidates with `no-cache`;
4. SPA navigation still falls back correctly;
5. repeated preload failure cannot reload-loop.

When probing origin via `127.0.0.1`, send `Host: socialzen.ahsanworks.com`. Without the production Host header, nginx may select the default server block and misleadingly return SPA HTML/200 even though the SocialZen virtual host is correct. Verify both the host-routed origin and the public CDN response; CDN cache headers may intentionally differ from origin headers.

Run the focused guard test, frontend typecheck, production build, and nginx syntax check. A build does not prove nginx behavior, and an isolated syntax pass does not prove live integration.

Remain read-only until the user explicitly authorizes implementation or deployment.