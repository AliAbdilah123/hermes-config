# Project workspace: explicit draft persistence

Use when changing SocialZen Project workspaces that create, edit, or remove child posts.

## Persistence boundary

- First identify the requested save scope. In a Project workspace, **Save means one project-level `Save Project` boundary**, not a Save button on every child post. Do not infer per-post persistence from existing post APIs.
- Treat the workspace as a staged editor: local additions, edits to persisted posts, destination changes, and pending removals stay in client state until `Save Project` is activated.
- Selecting local files may upload media immediately, but must not create canonical `posts` rows. Build one local unsaved draft per selected file and persist it only through `Save Project`.
- The ordinary `+ Add` action and “create posts from generated outputs” must also create local unsaved drafts. Do not call the project-post creation endpoint from either action.
- Existing persisted drafts must not PATCH while fields change. Include editable title/name and content in the project-save operation.
- On complete success, clear local additions and pending removals, then reload canonical project data. On failure, preserve all staged state so the user can retry without losing edits.
- Prefer one transactional backend project-save endpoint when the requirement says all project changes apply together. A frontend loop over PATCH/POST/DELETE starts only after the button, but can partially persist on mid-save failure and is not atomic. Reuse sequential endpoints only when partial application is explicitly acceptable.

## Local-file behavior

- A multi-select file input creates one independent draft per file, not one carousel draft.
- Initialize each draft name from the first 25 characters of its filename and allow editing before Save.
- Infer the initial post type from uploaded media (`VIDEO` to Reel, image to Photo), while retaining existing editor controls.
- Keep unsaved drafts out of scheduling until persistence succeeds.

## Deletion contract

- Render the delete control outside the collapsible editor panel so it remains available when the row is collapsed.
- Use a red trash-bin icon button with an accessible `aria-label` and title naming the post; do not rely on the icon as the accessible name.
- Require explicit confirmation naming the post.
- Clicking delete immediately removes either kind of row from the visible staged workspace.
- Deleting a local unsaved row is client-only and removes it from local additions.
- Deleting a persisted child adds its ID to a pending-removals set. **Do not call DELETE/archive from the trash button.** Apply it only inside `Save Project`.
- If the save fails, retain the pending-removals set and keep the row hidden so retry semantics remain truthful.
- **Archive is not removal unless reads exclude archived rows.** Any shared post fetch used by project detail/list responses must default to `status <> 'ARCHIVED'` (or equivalent). Otherwise a successful saved removal reloads the archived record and appears to undo deletion.
- Preserve archive semantics when history/recovery needs them; filter normal reads rather than physically deleting the row unless permanent deletion is explicitly required.

## API trust boundary

When project-post creation accepts uploaded media references:

- Allow only the intended cardinality for this flow (one media item per independently created draft).
- Validate media type and non-empty URL.
- Verify the referenced upload belongs to the authenticated user before linking it to a post.
- Keep post insertion, media insertion, copied project targets, and initial immutable version in one transaction.

## Focused verification

Leave frontend tests proving:

1. Selecting multiple files creates multiple local drafts with truncated names.
2. Add, generated-output selection, field edits, destination changes, and trash clicks issue no canonical write before `Save Project`.
3. There is one visible project-level save control and no per-post Save controls.
4. `Save Project` persists additions and edits, then applies queued removals.
5. Delete remains visible for a collapsed row, is an icon-only accessible control, hides the row after confirmation, and does not send DELETE until `Save Project`.
6. Unsaved delete is client-only.
7. A failed save retains staged additions, edits, and removals for retry.
8. If atomicity is required, a backend failure rolls back every project change rather than leaving a partially saved workspace.

Leave a backend regression test that creates a project child, DELETEs it, reloads project detail, and asserts the archived child is absent. This catches the false-success pattern where the write succeeds but the read model returns archived rows.

Run the focused workspace tests, TypeScript typecheck, production build, focused Go post/container tests, and `git diff --check`. Stage only feature-owned files in a dirty tree before commit/push.

## Live delivery gate

A pushed commit is not a live deployment. For this app, completion after a user asks for live behavior requires all of these artifacts to advance:

1. Build the frontend production bundle.
2. Publish the complete clean `dist/` directory to the Nginx-served SocialZen directory (use clean replacement semantics such as `rsync --delete`).
3. If backend code changed, rebuild the exact executable referenced by `socialzen.service`, install it, and restart the service.
4. Poll the local health endpoint until ready; an immediate restart result is insufficient.
5. Fetch cache-busted public HTML, resolve the emitted `ProjectWorkspace-*.js` hash, and confirm unique feature markers in that public bundle.
6. Confirm the service is active and local HEAD equals the pushed remote branch.

Do not report the live app as updated based only on source tests, build success, or `git push`.