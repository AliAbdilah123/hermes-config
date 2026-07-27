# Clean-build SPA preview and production promotion

Use this when an approved SPA preview depends on full-stack code or when the primary checkout contains unrelated local changes.

## Build provenance

- Identify the branch and cleanliness of every checkout explicitly; do not call a checkout “normal” when you mean the primary working directory.
- Build production from a fresh worktree at the exact candidate commit. A dirty checkout may contain untracked modules that hide an incomplete branch.
- If a committed module imports an untracked file, treat the branch as inconsistent. Repair that prerequisite in a separate minimal commit with focused tests; do not smuggle the file into a feature commit.
- Run commands from the actual package root. In a monorepo, verify where `package.json` or the Go module lives before invoking a build.

## SPA preview verification

An HTTP 200 does not prove the requested SPA route works: Nginx may return a production or fallback `index.html`, after which React renders its own Not Found page.

Verify all of the following:

1. The preview has a dedicated Nginx location with SPA fallback to the preview's own `index.html`.
2. Runtime basename/API-base injection matches the preview subpath.
3. Root and deep-link HTML reference the preview's hashed assets.
4. The served feature chunk contains a stable marker from the intended feature.
5. The authenticated API returns the expected data shape/count.
6. Where browser automation is available, inspect rendered text and interactions; never present HTTP-only checks as visual verification.

For backend-dependent previews, run a temporary API against a SQLite snapshot made with `.backup` or `VACUUM INTO`, never a raw live DB/WAL copy. Route only the preview API prefix to it. Keep preview writes isolated from production.

## Promotion sequence

1. Reproduce and repair clean-build blockers in an isolated integration worktree.
2. Keep prerequisite repairs and the approved feature in separate commits.
3. Run focused tests, relevant API tests, lint for changed files, and clean production builds.
4. Push the exact verified commit to the production branch.
5. Deploy API and frontend artifacts from that clean worktree; back up current artifacts first.
6. Verify service health, public hashed asset markers, and authenticated origin data.
7. Remove preview Nginx blocks/files and stop temporary processes only after production verification.
8. When removing Nginx blocks, inspect the actual active config and edit precise boundaries; do not rely on remembered formatting.

## Communication pitfall

After stating “understood” or giving a progress update, immediately continue tool work until the requested fix is verified. Do not stop at a status message unless blocked on a user decision. Explain safety gates in concrete repository terms: branch, directory, tracked/untracked file, and exact failing import—not only jargon such as “clean-build gate.”
