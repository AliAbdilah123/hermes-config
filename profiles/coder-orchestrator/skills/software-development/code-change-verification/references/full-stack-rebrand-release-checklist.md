# Full-stack rebrand release checklist

Use for product renames that cross source, runtime, filesystem, and public routing boundaries.

## Inventory before editing

Search tracked files and deployment configuration for every old form:

- Display name (`Old Product`)
- Package/repository slug (`old-product`)
- Local project directory
- Backend default product name and provider-facing messages
- Page titles, navigation, authentication copy, metadata, and favicon
- Package manifests and lockfiles
- Service unit name, description, working directory, environment path, and binary path
- Web-server route slug, static root, API proxy, root-mounted development domain, redirects, and cache rules

Inspect Git status first. Existing untracked databases, media, backups, plans, or generated binaries are not part of a branding commit unless explicitly requested.

## Apply the rename

1. Change user-visible branding consistently, including provider replies and backend defaults.
2. Change machine names only where they identify the project. Do not rename stable API contracts, database schema, provider IDs, or persisted data merely for cosmetic consistency.
3. Update both package manifest and lockfile.
4. Replace framework-default branding assets such as the favicon.
5. Rename the local directory only after file edits, then use the new path for all subsequent commands.
6. Add the change to the project's changelog.

Historical plans and audits need judgment: update them when they are active operational references; otherwise preserve historical wording. Never bulk-edit arbitrary untracked artifacts.

## Verify before release

Run the repository's complete applicable checks. A typical Go + Svelte workspace includes:

```sh
npm test
npm run check
go test ./backend/...
go vet ./backend/...
git diff --check
go build -o /tmp/<new-slug>-server ./backend/cmd/server
```

Choose the frontend base from the **browser-visible mount**, not the internal Nginx compatibility route. If `dev-<slug>…/` is root-mounted but internally rewritten to `/projects/<slug>/`, build the public artifact for `/` (no `BASE_PATH`). Building for `/projects/<slug>` can make SvelteKit `resolve()` and `goto()` emit a hidden internal path even when Nginx rewrites static asset URLs successfully.

If one artifact must serve both public root and legacy subpath URLs, verify that the framework genuinely supports that arrangement; otherwise publish separate builds or retire the compatibility path. Do not use broad JavaScript `sub_filter` rewriting as proof that framework routing state is correct.

Then search tracked source for obsolete display names and machine slugs. A changelog sentence that names the old brand is an intentional exception.

## Deploy atomically

1. Build with the final deployed base path, not the previous slug.
2. Stage static output in a sibling `.new` directory.
3. Install the backend binary under its canonical new name.
4. Update service paths and web-server routing together.
5. Validate web-server configuration before reload.
6. Reload service definitions, enable/start the new unit, and stop/disable the old unit.
7. Swap the staged static directory into place only after configuration validation.
8. Remove old public static output only after the new health check succeeds.

Preserve `.env`, databases, media caches, and other runtime state when renaming the project directory. Confirm the service now points to that preserved state.

## Public release evidence

Do not mark the rename complete from source/build evidence alone. Verify all of:

- New public root or login route returns `200`.
- Public API health returns `200` and expected JSON.
- A fresh browser renders meaningful DOM at the exact public root route and reaches the expected route after client navigation. Capture runtime exceptions; HTTP `200` plus loadable JS/CSS is insufficient because hydration or `goto()` can still crash into a blank page.
- Inspect `document.baseURI`, any rendered `<base>` element, and the framework's compiled base value. A reverse-proxy `sub_filter` can turn `<base href="/projects/<slug>/">` into `<base href="//">`; browsers may resolve that against `about:blank`, causing `new URL()` failures. Prefer removing an unnecessary HTML base tag and using framework-native path resolution.
- Deployed JavaScript contains the new brand and not the old brand; static HTML may not contain client-rendered text.
- New favicon is publicly reachable.
- New service is enabled and active.
- Old domain/path has the intended retirement behavior (`404` or redirect, according to the request).
- Local commit equals the pushed remote branch.

If browser automation is unavailable, HTTP-fetch the public HTML and referenced JavaScript assets and inspect those real deployed bytes. This is a fallback for branding verification, not a substitute for interaction E2E when behavior changed.
