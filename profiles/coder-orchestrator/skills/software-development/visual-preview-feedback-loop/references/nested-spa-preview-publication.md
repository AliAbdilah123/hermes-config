# Nested SPA preview publication

Use when a Vite-style SPA is served below a path such as `/previews/<name>/`.

## Build and publish

1. Discover the package root, bundler output directory, and public mount.
2. Build with the exact mount as the asset base, including a trailing slash when required:
   ```sh
   VITE_BASE=/previews/<name>/ npm run build
   ```
3. Before publication, assert `dist/index.html` points every entry script, module preload, and stylesheet into `/previews/<name>/assets/`; reject production prefixes such as `/projects/app/assets/`.
4. Publish from the package output directory under fail-fast semantics:
   ```sh
   set -eu
   rsync -a --delete apps/web/dist/ /var/www/html/app-previews/<name>/
   ```
   Do not append an unconditional success message after a copy command; a later successful command can otherwise mask the failed publication.

## Public proof

1. Fetch the exact cache-busted preview HTML.
2. Extract its referenced entry JS and CSS URLs.
3. Require those exact URLs to return 200 and appropriate MIME types.
4. Render the exact URL and inspect a screenshot. A root `200`, valid HTML shell, or healthy assets does not prove React mounted.
5. Exercise the requested interaction before declaring `READY FOR REVIEW`.

## Blank-page diagnosis

If the page is blank after a successful build, inspect public HTML first. A common cause is a preview HTML shell that references production-prefixed assets, loading a different bundle with an incompatible runtime basename. Rebuild with the preview base rather than patching application code or copying production assets into the preview namespace.
