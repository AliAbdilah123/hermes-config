# SPA subpath preview asset-prefix verification

When publishing an isolated SPA preview under a subpath:

1. Inspect the built `dist/index.html` before writing nginx/sub-filter rules.
2. Record the exact emitted asset prefix. It may already be production-prefixed (for example `/projects/<app>/assets/...`) rather than `/assets/...`.
3. Rewrite that exact emitted prefix to `/previews/<slug>/assets/...`. A generic `/assets/` rewrite will not match a production-prefixed build and can silently make the preview load production assets.
4. Fetch the public preview HTML and assert its script and stylesheet URLs are preview-prefixed.
5. Probe every referenced JS/CSS asset for HTTP 200 and the correct MIME type.
6. Fetch a deep preview route and assert it returns preview HTML with the injected preview basename/API-base marker, not production fallback HTML.
7. Compare the production HTML asset hash before and after publishing to prove production stayed unchanged.

A successful build and HTTP 200 on the preview root are insufficient; the public HTML must reference the preview bundle itself.