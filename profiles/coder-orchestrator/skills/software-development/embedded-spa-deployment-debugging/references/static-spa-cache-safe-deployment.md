# Cache-safe static SPA deployment

Use when a hashed-asset SPA is redeployed to an nginx leaf and some clients see a blank page while fresh Chromium renders correctly.

## Failure mode

A destructive sync such as `rsync --delete` publishes new `index.html` plus new hashed assets and immediately removes the previous hashes. A browser, intermediary, service worker, or CDN holding the previous HTML still requests the old JS/CSS. If nginx `try_files` falls back to `index.html`, the old JavaScript URL may return HTML with status 200; module loading then fails and the SPA appears blank.

Do not diagnose this from current HTML/assets alone. Test both generations:

1. Read the pre-deployment backup's `index.html` and extract its JS/CSS URLs.
2. Probe those exact old URLs publicly, recording status, MIME type, and body size.
3. Probe the current HTML and assets separately.
4. Render a cache-busted current route and collect runtime errors.
5. If fresh render works but prior hashes are absent or return `text/html`, classify this as deployment-generation incompatibility.

## Immediate recovery

Restore the previous hashed assets alongside the current generation from the deployment backup. Hashed filenames are immutable, so retaining them is safe. Verify every old and current asset returns 200 with its real MIME type (`application/javascript` or `text/css`), never SPA HTML.

## Durable deployment contract

- Serve entry HTML with `Cache-Control: no-cache, no-store, must-revalidate` (or at least revalidation).
- Serve immutable hashed assets with long-lived cache headers.
- Keep at least the immediately previous asset generation during rollout; do not use an unqualified `rsync --delete` against the asset leaf.
- If cleanup is needed, prune only asset generations older than the compatibility window after confirming no referenced HTML generation can remain cached.
- Prefer an exact `location = .../index.html` cache policy plus a route-level no-cache policy for SPA fallbacks.
- Ensure missing asset URLs do not silently become HTML. Probe status, MIME type, and a JS/CSS marker.

## Verification gate

1. `nginx -t`, then reload.
2. Previous and current JS/CSS hashes all return 200 with correct MIME types.
3. Cache-busted public Chromium render contains route-specific content.
4. Browser stderr has no uncaught exception, syntax error, or failed module load.
5. Inspect the final filesystem so a later deployment command cannot immediately delete the compatibility assets again.

HTTP 200 for the page is insufficient; cached-generation compatibility is the relevant behavior.