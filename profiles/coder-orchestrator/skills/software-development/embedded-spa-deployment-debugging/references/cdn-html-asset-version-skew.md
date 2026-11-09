# CDN HTML/asset version skew

Use when a deployed page shows the current static shell but dynamic content disappears after a frontend release.

## Signature

- Public HTML contains the new DOM structure.
- The API is healthy and returns expected records.
- Public JS/CSS under unchanged URLs differs from the origin/local service.
- Old JavaScript queries removed nodes or binds obsolete controls, throws during startup, and leaves only static headings.
- CDN headers often show `HIT`, nonzero `Age`, and long `max-age`.

## Diagnosis

Fetch public HTML, JS, and CSS separately and preserve headers. Fetch the same assets from the origin, then compare sizes, checksums, and unique release markers. Probe the API independently. Syntax success from `node --check` does not prove that cached JavaScript matches the current HTML.

```sh
curl -fsS -D /tmp/public.headers https://example.test/app.js -o /tmp/public.js
curl -fsS http://127.0.0.1:8080/app.js -o /tmp/origin.js
sha256sum /tmp/public.js /tmp/origin.js
curl -fsS https://example.test/api/items
```

Inspect recent frontend changes for DOM changes shipped under unchanged asset paths.

## Root fix

Publish HTML and dependent JS/CSS as one coherent release. With long-lived CDN caching, change asset URLs using content hashes, build fingerprints, or a versioned filename. If the backend allowlists static paths, update that router and its integration tests in the same change.

A restart alone cannot invalidate already cached public assets. Do not make “clear your browser cache” the product fix. Prefer fingerprinted filenames over permanent query-string busting when supported.

## Verification

1. Rebuild the executable when assets are embedded, then restart/deploy it.
2. Confirm public HTML references the new asset names.
3. Confirm public and origin asset checksums match.
4. Run a fresh public browser E2E at the reported viewport.
5. Assert dynamic records exist in rendered DOM; HTTP 200 is insufficient.
6. Record the fix in the changelog, then commit and push when required.
