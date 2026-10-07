# Virtual asset Library and standalone Creation Studio

Use when implementing reusable media selection across posts, Projects, uploads, and AI generation.

## Domain boundaries

- **Library is a read/organization projection, not filesystem storage.** Its folders are one-level virtual groupings; never move or duplicate underlying files merely to represent a folder.
- All media attached to saved, non-archived posts is visible in Library.
- Media from a standalone post (`project_id IS NULL`) appears at Library top level.
- Media from a Project child post appears in a virtual folder whose identity is the stable Project ID and whose label is derived from the current Project title. Do not persist a copied project-folder name: project renames must appear automatically without a synchronization job.
- User-created folders are also one-level virtual collections. Reject parent-folder input rather than silently nesting.
- Creation Studio is a separate top-level workflow, not an accordion or panel inside Project Workspace.
- Each Creation Studio session owns a Library-visible virtual folder; completed outputs appear there and remain reusable independently of whether they become posts.
- Project Workspace consumes finished assets through **Add from library**, with folder browsing and multi-select. Selection creates staged local drafts and must preserve the existing project-level Save boundary.

## Minimal implementation stance

Prefer deriving automatic folders at query time:

- Project folder: join `projects -> posts -> post_media` and use `projects.id/title`.
- Top level: query owned `posts.project_id IS NULL -> post_media`.
- Studio folder: join the stable session record to its generation jobs/items.
- Persist only user-created collection membership and Creation Studio session identity; do not create redundant records for project-derived folders.

If legacy generation tables require a Project foreign key, an internal hidden Project may be used as a compatibility bridge, but exclude it from normal Project lists and expose only the Creation Studio session publicly. Mark this as transitional and avoid letting publishing semantics leak into Studio UX.

## Trust and lifecycle rules

- Every Library query and selection endpoint must scope by authenticated owner.
- Return only usable saved-post media and completed generation outputs.
- Do not infer ownership from a client-supplied URL; resolve stable asset/media IDs server-side when canonical persistence occurs.
- Archived posts should not repopulate normal Library views unless archive browsing is explicitly designed.
- Project rename behavior must be covered by a regression test proving the same virtual folder ID receives the new label.

## TDD checks

Backend tests should prove:

1. standalone saved-post media appears at top level;
2. Project media appears under the Project-derived folder;
3. renaming a Project changes the folder label without moving data;
4. nested folder creation is rejected;
5. foreign-user posts, projects, sessions, and assets are absent;
6. completed Studio outputs appear in the matching session folder;
7. hidden compatibility Projects do not appear in Project lists.

Frontend tests should prove:

1. Library switches between top level and one-level folders;
2. Add from library opens an accessible modal and supports multi-select;
3. selected assets become staged local drafts without a canonical write before Save Project;
4. Creation Studio creates/opens a session before requesting generation;
5. empty, loading, failure, image, and video states remain usable.

## Delivery gates

- Remove dead embedded-Studio rendering rather than hiding it behind a constant-false branch. Also remove the now-unused state, polling, API calls, and types; typecheck catches partial cleanup.
- When a feature corrects a previously documented product model, update the canonical `.hermes/plans/` source, its paired plan/design HTML, supporting alternatives, and `CHANGELOG.md` in the same delivery. Add a clear superseding note when historical alternatives are intentionally retained.
- Publish changed review HTML through `/usr/share/nginx/html/prds/` symlinks, ensure source mode `644`, run `nginx -t`, and verify both HTTP 200 and a stable marker from the updated content at `https://dev.ahsanworks.com/prd/<file>`.
- Run focused backend tests, focused frontend tests, typecheck, production build, and `git diff --check`.
- A full-suite unrelated baseline failure must be reported separately and does not replace focused passing evidence.
- Deploy the exact backend binary used by the service and the complete clean frontend `dist/`.
- Read the service's actual listening port from runtime evidence before probing health.
- Verify frontend deployment against the canonical development host `https://dev-socialzen.ahsanworks.com`: compare the live and local `index-*.js` basenames, resolve the relevant lazy chunk from the live index, and assert both a new stable marker and absence of removed UI markers. Do not use another hostname as deployment proof merely because it returns HTTP 200; it may serve a different cached build.
- Do not claim public E2E when only HTTP 200, health, or bundle checks succeeded. If authenticated browser interaction was not completed, state that explicitly and keep readiness below READY.
