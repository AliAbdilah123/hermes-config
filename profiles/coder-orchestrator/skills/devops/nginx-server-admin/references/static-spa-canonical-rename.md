# Canonical rename of a path-mounted static SPA

Use this when renaming both a project and its public `/projects/<slug>/` URL.

## Rename surface

1. Start from a clean Git status and record the current commit/remotes.
2. Search tracked source (exclude `node_modules` and `dist`) for the old slug, display name, title, favicon initials, package metadata, documentation headings, browser-test URLs, and local-storage namespaces.
3. Rename the source directory only after identifying all active paths. Run later commands from the new directory.
4. Update package manifest and lockfile root package names together.
5. Update visible identity at desktop and narrow mobile widths; retaining only a new favicon/initial is insufficient when the requested project name must remain visible.
6. If changing the storage namespace, treat loss of old demo state as intentional; add migration only when user data must carry across.

## Nginx cutover

1. Back up the active config.
2. Replace the exact old location block with the new slug, alias, and SPA fallback.
3. Explicitly disable the old exact and prefix routes when the old URL must be removed:

```nginx
location = /projects/old-slug { return 404; }
location ^~ /projects/old-slug/ { return 404; }
```

4. Preserve literal nginx variables such as `$uri`: write multiline edits through a single-quoted/temporary script, never through a shell-expanded payload.
5. Read the changed block back, run `sudo nginx -t`, then reload.

## Build and deployment

1. Run tests, lint, and typecheck from the renamed package root.
2. Build with the new Vite base, e.g. `vite build --base=/projects/new-slug/`.
3. Assert generated HTML contains the new prefix/title and no old slug.
4. Deploy with `rsync --delete` to the new leaf directory.
5. Remove the old deployed leaf only after the new nginx config validates and the new build exists.

## Public verification

- Cache-bust every probe with a unique timestamp.
- Verify new root HTML, title, referenced JS/CSS URLs, correct MIME types, and a deep SPA route.
- Require old root and old deep routes to return the intended terminal response (usually 404, not the fallback SPA).
- Run browser workflows at representative widths and assert zero console/page/network errors and horizontal overflow.
- Visually verify the new name on desktop and narrow mobile chrome.
- For fixed overlays/docks, use viewport screenshots and DOM geometry; full-page stitching can falsely depict overlap or uncovered regions.
- Commit only the exact verified rename. Push only when a real remote exists.
