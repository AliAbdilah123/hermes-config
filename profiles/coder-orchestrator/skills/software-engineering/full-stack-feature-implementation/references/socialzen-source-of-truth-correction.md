# SocialZen source-of-truth correction

Use this note when a project is migrated to a known local stack but must preserve upstream application/UI behavior.

## Lesson

For SocialZen/Scheduling-Post, the cloned git repo/current upstream commit is the source of truth. A prior migration accidentally copied frontend files from a separate Brand Organizer working tree because that project already had a Go/SQLite stack. This caused unrelated UI/content changes (for example `Sidebar.tsx` nav and styling) that were not required by the stack migration.

## Corrective workflow

1. Compare the migration commit against the previous git commit first:
   - `git diff --stat HEAD^ HEAD`
   - `git diff --name-status HEAD^ HEAD`
   - inspect suspect files such as `apps/frontend/src/components/Sidebar.tsx`.
2. If a different project was used as a donor, check whether files are exact copies of that donor. Treat exact-copy frontend matches as suspect unless explicitly requested.
3. Restore application/UI files from the project’s own git source-of-truth (`git checkout <source-commit> -- apps/frontend`) and reapply only necessary seams:
   - local auth/API wrappers required by the new backend
   - Vite `base`/proxy and env defaults for the deployment slug
   - minimal test/type fixes caused by those integration seams
4. Re-run the complete verification suite and redeploy the corrected build.
5. Report remaining diffs as intentional categories, not as a broad “frontend migrated” claim.

## Expected intentional diffs after correction

- Backend stack replacement (`apps/backend` removed, `apps/backend-go` added).
- Root/dev scripts updated to run Go backend.
- Frontend API/auth integration seams only.
- Deployment slug/base path updates (`/projects/socialzen`).

## Pitfall

A passing build/test suite is not enough to prove migration correctness if another project’s UI was copied. Always audit semantic diffs against the project’s own previous commit/current upstream source.
