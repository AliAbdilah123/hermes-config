# Data-backed gallery production handoff

Use after approval of an admin-managed image-gallery prototype.

## Contract

- Persist gallery items as ordered child records, not a delimited field on the parent. A minimal record has `id`, parent ID, image URL, position, and creation timestamp; enforce the parent relationship and a deterministic `(parent_id, position)` order.
- Return gallery records in the existing public parent-detail DTO so the public carousel does not need a second catalog fetch.
- Keep carousel order explicit: parent thumbnail first, then gallery records. Remove product/package/catalog-derived slides rather than mixing both sources.
- Mutations require parent-admin authorization. Validate stored image URLs against the application's upload namespace; do not accept arbitrary external URLs merely because the UI normally uploads first.
- Reuse the existing image upload endpoint and file validation. If upload and gallery-record creation are separate requests, acknowledge the orphan-file boundary; add transactional cleanup only when storage lifecycle requirements justify it.

## TDD slices

1. API test: unauthorized/forbidden mutation, invalid URL, ordered persistence in parent detail, deletion scoped to the parent.
2. UI test: add control is the literal first list item; upload → persist → render → remove works through real client contracts.
3. Carousel test: thumbnail precedes gallery images and product/package images are absent.
4. Structural CSS assertion: three desktop columns, 4:3 items, and named narrow-screen breakpoints. Follow with rendered viewport QA; source assertions alone are not visual proof.

## Verification and deployment

- Run focused API tests, focused UI tests, changed-file lint, typecheck/production build, and repository suites independently. Preserve exact failing test names and assertions when unrelated failures remain; a truncated full-suite log is not sufficient evidence.
- Confirm the backend module directory before running language tooling in a monorepo (for example, run Go commands beside the relevant `go.mod`).
- A scoped commit does not make a dirty-workspace build scoped. After committing only feature files, create a clean worktree/check-out at that commit and rebuild both backend and frontend there. Deploy only those clean artifacts.
- Restart the backend, check service health, verify the public HTML references the new asset hash, fetch that exact public asset, and probe the authenticated gallery route in-browser. Bundle-string presence proves publication, not interaction or visual correctness.
- Never claim “without errors” when a requested suite has a known failure. Separate feature-green checks from unrelated failures and either resolve the blocker or state the acceptance gap.
