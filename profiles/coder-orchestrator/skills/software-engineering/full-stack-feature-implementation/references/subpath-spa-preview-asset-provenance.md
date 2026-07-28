# Subpath SPA preview asset provenance

Use for Vite/React previews mounted below `/previews/<slug>/` while production stays at `/`.

## Build-output reality

Generated `index.html` may reference `/assets/...` or a production-prefixed path such as `/projects/<app>/assets/...`. Inspect `dist/index.html`; do not assume one prefix.

## Publication pattern

In the preview Nginx location, rewrite every asset prefix actually present to `/previews/<slug>/assets/`. Inject the app's supported router basename and an explicit API base. If the preview points to a live API, label that clearly and avoid destructive QA.

## Independent gates

1. Preview root and every required deep route return HTTP 200.
2. Returned HTML references `/previews/<slug>/assets/...` rather than production assets.
3. The rewritten main JS/CSS assets return HTTP 200.
4. Injected basename and API-base values are exact.
5. Production and preview HTML reference distinct main bundle URLs, proving production remains unchanged.
6. Browser-check rendering and console when available. If unavailable, report only HTTP/deep-route/asset evidence; do not claim visual or console verification.

## Pitfall

A preview deep route can return HTTP 200 while its HTML still points to production assets. Deep-route status and asset provenance are separate verification gates.