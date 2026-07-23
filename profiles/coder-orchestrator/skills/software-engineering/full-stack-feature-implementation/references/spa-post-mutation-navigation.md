# SPA post-mutation navigation regressions

Use when a successful mutation (join, enroll, subscribe, claim) leaves the user on the wrong route, especially after removing an explicit redirect did not change observed behavior.

1. Trace every navigation source: the mutation handler, returned redirects, effects reacting to refreshed state, modal callbacks, and parent success handlers.
2. Add a router-level interaction test with both the intended page and wrong destination registered. Click the real CTA, await the mutation, assert the intended page remains rendered, and assert the wrong route does not.
3. When the requirement is “stay on this detail page,” prefer an explicit canonical post-success route if refreshed state may trigger competing navigation: `navigate(canonicalDetailPath, { replace: true })`. Apply it only to immediate success; approval-pending flows may differ.
4. Rebuild and publish. Verify source → generated bundle → deployed file → public cache-busted response. A source test cannot detect a stale live bundle/CDN response.
5. If old behavior persists, gather browser/network evidence before adding another redirect; distinguish a code-path failure from stale deployment/cache.

Verification:
- Canonical: focused interaction test, then project build.
- Deployment: compare generated/deployed asset hashes and fetch public cache-busted HTML/assets.
- Ad-hoc fallback: create `/tmp/hermes-verify-*` with `mktemp`, assert the canonical route exists and the old success-to-wrong-route branch does not, run it, remove it, and label the result ad-hoc rather than suite green.

Pitfall: removing one known bad navigation is weaker than establishing the intended postcondition. A refresh callback or state-driven effect can still move the route. Test and enforce the final route, not merely the absence of one old call.
