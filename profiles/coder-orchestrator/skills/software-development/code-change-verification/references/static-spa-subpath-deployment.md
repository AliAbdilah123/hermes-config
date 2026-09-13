# Static SPA subpath deployment verification

Use when a Vite/React SPA is served below a path such as `/projects/app/` rather than at the origin root.

## Failure pattern

The public HTML can return HTTP 200 while the app is blank because the generated document points to root-relative assets such as `/assets/index.js`. The real files may exist only at `/projects/app/assets/index.js`. HTTP success for `index.html` is therefore not render evidence.

## Minimal fix and verification

1. Inspect the bundler config and set the deployment base explicitly (for Vite, `base: '/projects/app/'`).
2. Rebuild from the package root.
3. Inspect generated `dist/index.html`; require JS and CSS URLs to begin with the deployed prefix.
4. Publish the rebuilt `dist/` to the exact nginx document root.
5. Probe both candidate asset paths:
   - root `/assets/...` should not be relied on;
   - prefixed `/projects/app/assets/...` must return the correct JavaScript/CSS MIME type.
6. Run the exact public browser route with a unique cache-buster, wait for app chrome, and exercise the requested behavior. Capture console, page errors, and failed requests.

## Test-boundary pitfall

Do not import `vite.config.ts` into a jsdom application test merely to assert `base`. Loading Vite/esbuild inside the test environment can fail on runtime invariants unrelated to the product. Prefer a directly executed build artifact assertion (`grep` or HTML parsing against `dist/index.html`) inside the final verification script. This checks the actual emitted contract rather than configuration intent.

## Browser harness portability

Temporary E2E scripts resolve Node packages relative to their own location. If the script lives under `/tmp`, either place it in the package root or deliberately provide module resolution to the project's installed `playwright-core`; classify import failures as harness setup, not product failure. Discover the system Chromium executable with `command -v chromium-browser || command -v chromium || command -v google-chrome` before launch instead of assuming one path.

## Evidence boundary

A prefixed asset URL and HTTP 200 prove publication transport. Only a rendered browser flow on the exact public subpath proves routing and behavior. If the app has role selection rather than account authentication, report role-based public E2E accurately; do not call it authenticated E2E.
