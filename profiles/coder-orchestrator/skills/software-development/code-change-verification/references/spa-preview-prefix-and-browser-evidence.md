# SPA preview prefix and browser evidence

## Asset-prefix discovery

Before writing preview-server substitutions, inspect the emitted `dist/index.html`. Do not assume the build references `/assets/`; an artifact may retain its production prefix such as `/projects/<app>/assets/`.

Rewrite the prefix actually present to `/previews/<slug>/assets/`, then publicly fetch the transformed HTML and extract all local JS/CSS URLs. Every extracted asset must return its real MIME type rather than an SPA HTML fallback.

Use a unique query parameter when checking newly changed HTML through a CDN so the evidence is fresh.

## Evidence boundary

HTTP 200, correct transformed HTML, valid asset MIME types, and deep-route SPA fallback prove publication plumbing only. They are not browser-render verification.

For browser evidence:

1. Open the exact public deep route.
2. Assert the requested content is present in rendered DOM and generic error/not-found content is absent.
3. Inspect runtime console errors.
4. Capture a screenshot and verify the output file exists and is non-empty before citing it.
5. If authentication or unavailable preview data prevents the requested feature state from rendering, report that boundary explicitly; do not call transport checks browser verification.

## Staging new files

`git diff --name-only` excludes untracked files. Before commit, inspect `git status --short`, explicitly stage intended new files, and recheck status. After push, compare local HEAD with the remote feature-branch SHA.
