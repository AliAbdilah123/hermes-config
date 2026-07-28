# SPA subpath and exact-route verification

Use this when publishing an isolated SPA preview under a nested URL such as `/previews/<slug>/`.

## Routing contract

A copied build directory is not enough. The preview needs all three layers aligned:

1. Build asset base points at `/previews/<slug>/`.
2. Client router basename is injected as `/previews/<slug>/`.
3. The web server has a dedicated preview location with an SPA fallback to that preview's own `index.html`.

Without (2) or (3), asset probes may return 200 while React renders `Page not found`, or the production SPA fallback may silently answer the preview URL.

## Verification contract

Verify in increasing strength:

1. Root preview HTML contains the preview basename.
2. Hashed JS/CSS URLs are under the preview path and return correct MIME types.
3. A preview deep route returns the preview HTML, not production HTML.
4. Render with a real browser and assert `Page not found` is absent.
5. For authenticated dashboards, establish the required seeded/login state and render **every exact route named in the request**. Check route-specific content and requested interactions; the public landing page is not evidence for Sessions, Members, Analytics, Purchases, Audit Log, or Settings.
6. Capture console/runtime errors and fail verification on relevant errors.

## Common false positives

- HTTP 200 from a production `try_files` fallback.
- Correct assets with router basename still set to `/`.
- A working landing page while an authenticated tab still crashes.
- Unit tests and build passing while the deployed API/backend is not the code under review.

## Completion rule

Do not send a preview link as working until source → build → server route → exact served bundle → exact requested route/state has been traced and exercised.