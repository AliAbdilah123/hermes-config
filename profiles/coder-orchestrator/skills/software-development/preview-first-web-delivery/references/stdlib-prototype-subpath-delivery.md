# Stdlib frontend prototype delivery under an nginx subpath

Use this for dependency-light prototypes built as plain HTML/CSS/JS plus a Python stdlib server shell.

## Portable frontend contract

- Use hash routing (`#/route`) when nginx serves the app under a project subpath and no server-side route semantics are required.
- Reference sibling assets relatively (`./styles.css`, `./app.js`), not from `/`, so the same files work through the Python shell and `/projects/<slug>/`.
- Keep mock data/state in frontend memory and label it visibly as demo-only.
- Limit the shell backend to static serving, SPA fallback, and an explicit JSON health endpoint; unknown `/api/*` routes must return JSON 404 rather than SPA HTML.

## Verification sequence

1. Run focused stdlib tests for health JSON, static HTML, SPA fallback, and unknown API behavior.
2. Run `python3 -m py_compile` and `node --check` where available.
3. Publish with `rsync --delete` to the exact project leaf, never a shared ancestor.
4. Verify public HTML, JS, and CSS separately, including MIME types and a deep-route fallback.
5. Run the real public flow in a mobile browser viewport and collect console/page errors.
6. Inspect a screenshot, but treat visual-model findings as hypotheses. Confirm suspected fixed-position gaps or overlap using browser geometry (`getBoundingClientRect`, viewport height, and computed styles) before editing CSS.
7. If source/deployed files changed but public computed styles remain old, cache-bust the CSS URL in HTML and verify the exact public marker before rerunning E2E.
8. After any visual correction, rerun focused tests, republish, and repeat the complete public browser flow from the final state.

## Common traps

- A successful behavior flow can still hide a favicon/resource 404; embed a data-URL favicon for portable prototypes or identify the exact failed request before dismissing console errors.
- A screenshot can appear to show space below a fixed bottom nav due to capture framing. Require geometry evidence such as `viewportHeight - (nav.y + nav.height) == 0` before patching.
- Query cache-busting the page does not necessarily refresh a separately cached stylesheet. Version the stylesheet URL itself.
- A new local repository may have no remote. Commit and publish can still succeed, but report push as unavailable rather than implying it happened.
