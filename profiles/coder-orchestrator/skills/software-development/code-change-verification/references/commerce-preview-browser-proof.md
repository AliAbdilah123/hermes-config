# Commerce preview browser-proof checklist

Use after backend payment tests pass and before sharing any commerce preview.

## Failure pattern

A subpath-mounted SPA can route ordinary API calls through a runtime-aware client while checkout uses direct `fetch()` with a build-time `/api` fallback. Direct API scripts pass, but browser completion fails because the webhook bypasses the preview API.

## Required proof

1. Start from the real Pay button in a signed-in browser.
2. Capture quote, checkout, completion/webhook, return/wallet, and notification requests.
3. Correlate every browser request with preview API logs; direct `curl` is not browser proof.
4. Assert every internal request uses the exact preview API prefix.
5. Inspect the deployed bundle for runtime API-base consumption and the completion route.
6. Confirm paid state, exact-once benefits, duplicate-completion idempotency, and one actionable payment notification.

## Regression test

Set the runtime API base (for example `window.__API_BASE__`) to a preview prefix, click Pay, and assert `fetch` received the exact preview-prefixed webhook URL plus POST options. Never assert only that `fetch` was called: the wrong root URL satisfies that weak assertion.

## Preferred implementation

Use the shared API client. If raw `fetch` is necessary, derive its base from the same runtime source before build-time defaults. Preserve the production fallback.
