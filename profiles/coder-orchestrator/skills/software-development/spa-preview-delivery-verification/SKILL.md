---
name: spa-preview-delivery-verification
description: Publish and verify isolated SPA previews on subpaths without false-positive HTTP checks, production fallback leaks, router-basename errors, or untested feature routes.
version: 1.0.0
---

# SPA Preview Delivery Verification

Use this skill when publishing or validating a React/Vue/Svelte/other client-routed SPA under a non-root preview path such as `/previews/<slug>/`.

## Core rule

A preview is not working merely because its URL returns HTTP 200. A production SPA fallback can return production `index.html` for an unknown preview path, and an asset URL can return HTML with status 200. The only acceptable proof combines route configuration, asset MIME checks, and real-browser rendering of the exact affected feature route.

## Workflow

1. **Isolate the artifact**
   - Build into or copy to a preview-only directory.
   - Do not overwrite production files.
   - Record production asset hashes before and after when production and preview share a host.

2. **Build for the exact public subpath**
   - Set the bundler base to `/previews/<slug>/`.
   - Set the intended API base explicitly.
   - Confirm generated HTML references preview-prefixed hashed assets.

3. **Give the preview its own web-server route**
   - Add an explicit highest-priority location for `/previews/<slug>/`.
   - Serve files from the preview directory.
   - Make `try_files` fall back to the preview's own `index.html`, never production `index.html`.
   - When the frontend derives API URLs from the bundler base, add a more-specific `/previews/<slug>/api/...` proxy before the SPA alias. Without it, the SPA fallback can return `index.html` with HTTP 200 for API/session requests and silently redirect authenticated checks to sign-in.
   - Validate configuration before reload.

4. **Set the client router basename**
   - Inject or configure `/previews/<slug>/`, not `/`.
   - Derive the deep route from the current router or navigation source; never guess it from a role, page title, or URL convention.
   - Confirm both preview root and that real application route contain the preview basename.

5. **Verify transport deterministically after publishing**
   - Treat build + copy + verification as one transaction; pre-copy checks do not prove the public artifact.
   - Re-probe root, deep route, emitted assets, and API immediately before telling the user the preview is ready; files or ad-hoc processes can disappear after an earlier successful check.
   - If the user reports a blank page, `500`, or missing preview, restore/rebuild and reverify it proactively after identifying the cause—do not stop at an explanation.
   - Preview root: HTML 200. Fetch the public HTML and extract the asset URLs it actually emits.
   - Actual hashed JS: JavaScript MIME, not HTML.
   - Actual hashed CSS: CSS MIME.
   - Real application deep route: preview HTML 200.
   - API health path and one feature API path: expected API response/auth behavior, not SPA HTML or `502`.
   - Ensure the isolated API is supervised or otherwise demonstrably remains listening throughout the review period; an expired ad-hoc process makes the preview incomplete.
   - Treat HTTP 200 on an unknown SPA route only as fallback-routing proof, never application-route proof.

6. **Verify rendering in a real browser**
   - Open the same source-derived public route at desktop and mobile widths.
   - Assert route-specific application text is present.
   - Assert `Page not found` and equivalent error-page text are absent.
   - Check uncaught exceptions and relevant console errors.
   - If the primary browser harness cannot launch, use an already-installed browser executable in native headless mode (`--dump-dom`, `--screenshot`, and captured stderr) rather than downgrading to HTTP-only verification.

7. **Verify the requested feature, not merely the homepage**
   - For authenticated work, establish a suitable test session or fixture.
   - If the preview uses an isolated database cloned from a live SQLite application, create it with SQLite's `.backup`/backup API rather than copying an arbitrary nearby `.db` file. Confirm the copy contains the real authentication tables and a plausible account count before starting the preview API.
   - Exercise authentication through the **public preview API path**, not localhost: sign up or use a dedicated review account, capture `Set-Cookie`, call the session endpoint with that cookie, sign out, sign back in, and confirm the protected preview route renders. A login form rendering is not authentication verification.
   - Navigate to the exact changed tab/page.
   - Reproduce the original payload shape, including nullable collections and empty states.
   - Exercise the interaction and assert the original error is absent.
   - For layout/theme changes, inspect the rendered hierarchy at multiple widths; source-code ownership alone is not proof.

8. **Report evidence precisely and preserve continuity**
   - State which exact routes, interactions, payload cases, and viewport sizes were exercised.
   - Distinguish routing smoke tests from feature verification.
   - Do not describe the preview as approved or production-ready until the affected feature route passes.
   - Never imply that verification is still running after the browser/process has stopped. If work is paused, say it is paused and resume it immediately when asked; use a tracked background process with completion notification for genuinely ongoing checks.

## Required regression fixtures

When the bug is collection-related, include explicit fixtures for:

- field omitted;
- field set to `null`;
- empty array;
- populated array.

Normalize data at the API/client boundary where practical; still test every downstream `.filter`, `.map`, `.length`, and iteration path implicated by the original stack trace.

## Pitfalls

- `curl -I` proves transport status, not application identity.
- Building with `base: "/"` for a subpath preview and relying on router/API injection still leaves HTML pointing at `/assets/...`; those requests can load production assets or fail blank. Build with the exact preview prefix and assert the emitted `src`/`href` values before publishing.
- Root-relative assets can silently hit production routes.
- Correct asset MIME types do not prove the router basename is correct.
- A working homepage does not prove an authenticated dashboard tab works.
- Finding theme tokens in a shared shell does not prove the visible theme begins above the tabs.
- Fixing one nullable field does not prove adjacent nullable collections are safe.
- Do not publish a review link—or claim it is published, ready, or done—before post-publish asset/API probes and browser rendering of the exact URL pass; build success and successful file copy are not completion evidence, and repeated broken links destroy trust.

## Supporting detail

See `references/subpath-spa-proof-checklist.md` for a concise reusable verification checklist and evidence format.
