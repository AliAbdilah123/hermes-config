# Embedded Go SPA: static assets, fallback, cache busting, and browser proof

Use when a Go service embeds a root-mounted HTML/CSS/JS dashboard with `embed.FS` and serves it behind nginx/CDN.

## Routing contract

Do not rewrite every non-API request to `/` before `http.FileServer`: that returns `index.html` for JavaScript and CSS paths, often with HTTP 200. The shell renders, but no application code runs.

Route in this order:

1. `/api/*` to API handlers.
2. Exact known assets to the embedded file server without rewriting their paths.
3. Remaining GET/HEAD paths to `/` for SPA fallback.
4. Reject unsupported methods.

Prefer immutable/versioned asset names (for example, `orchestrator-v1.js`) or content hashes. If a CDN has cached HTML at an old asset URL, fixing origin routing alone may not repair clients until expiry; publish a new asset filename and update `index.html`.

## Verification ladder

1. Build and restart the final binary so embedded files are fresh.
2. Fetch each asset from loopback and public HTTPS.
3. Assert response MIME and parseability, not just status:
   - JS body must pass `node --check`.
   - CSS must not begin with HTML.
   - API paths must decode as JSON.
4. Render the public URL in a real browser and assert populated DOM, not only the shell title.
5. Exercise mobile dimensions, drawer state, and horizontal overflow.
6. Capture console/runtime exceptions.

A useful failure signature is: `index.html` loads, resource timing shows the JS URL, but project options/cards remain empty and the fetched JS starts with `<!doctype html>`.

## Headless-browser fallback

If the primary browser wrapper is unavailable, use an installed headless Chromium with a remote-debugging port and Chrome DevTools Protocol. Create a fresh target, enable `Page` and `Runtime`, wait for load, evaluate DOM assertions, set mobile metrics, capture console exceptions, and optionally save a screenshot. This is still browser E2E evidence; report the mechanism accurately.

## Release check

After commit, rescan any Git-derived dashboard state so worktree IDs and dirty flags reflect the committed SHA rather than the pre-commit tree.
