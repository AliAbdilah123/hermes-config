# Project containers with multiple independently scheduled posts

Use when changing SocialZen's Project concept from “one post sent to multiple destinations” into a container of multiple posts.

## Domain boundary

- Add a real `projects` aggregate owned by the user.
- Keep `posts` as the canonical independently publishable unit and add nullable `posts.project_id`.
- Keep `project_versions.project_id` and `publication_runs.project_id` meaning **post ID** unless doing a separately approved publishing rewrite. Renaming those columns during this feature risks breaking queue, retry, analytics, and history.
- Existing Project-shaped posts backfill to a same-ID container containing that post. Preserve post/media/target/version/run/analytics identities. Standalone regular posts remain unlinked.
- Protect same-owner project/post linkage at both API and database boundaries.

## Workspace and scheduling

- The workspace lists child drafts and supports one schedule per post.
- Bulk scheduling is intentionally partial-success: each eligible post uses the existing preflight, quota, immutable version, publication run, targets, and queue path; return one explicit result per requested post.
- Make the bulk request replay-safe. Require a validated client idempotency key, persist `(project, user, key, request hash, exact response)`, return the exact response for identical replay, and return `409` if the key is reused with another payload.
- Concurrent same-key requests must converge on one durable response and one publication run.
- Frontend scheduling should retain a stable key for the same payload across transport retries, use another key when payload changes, and rotate only after a confirmed response.

## AI generation boundary

- No configured provider means `503 GENERATION_UNAVAILABLE`; never silently fabricate provider output in production.
- Mock image/video output is allowed only in development/test and must be visibly labelled placeholder/mock output.
- Persist project-scoped jobs and items with queued/generating/completed/failed states. Preserve completed outputs when other items fail; retry failed items only, with an attempt ceiling.
- Validate provider outputs before storage: bounded response/media size, allowed content type, decoded image dimensions/completeness, and probed MP4 video structure.
- Use durable database coordination for multiple backend instances:
  - schema-enforced one-active-job-per-project admission;
  - atomic worker claim with `lease_owner` and `lease_expires_at`;
  - only reclaim expired work;
  - do not mark all generating work failed during every migration/startup;
  - never overwrite completed items during stale recovery.

## Verification and release gates

1. Migration tests: idempotency, legacy graph preservation, standalone posts, ownership constraints.
2. Backend tests: multiple children, atomic asset-to-post batches, partial schedule results, identical replay, changed-payload conflict, concurrent same-key requests, generation admission, lease claim, live-lease preservation, stale recovery, failed-only retry.
3. Frontend tests: workspace loading/empty/error states, asset selection, child editing links, independent schedule fields, request-key lifecycle, mobile/keyboard accessibility.
4. Run focused Go and frontend tests, typecheck, build, and diff checks. Separate unrelated baseline suite failures from feature failures with evidence.
5. Deploy with backend binary and database backup, then verify service restart and live schema.
6. Authenticated public E2E must create a Project, enter the actual workspace route (exclude `/projects/new` from broad URL matching), add at least two child drafts, reload, confirm both schedule controls, verify production generation mode, and assert zero console/page/network errors.
7. Clean disposable test users through owner cascade after E2E. Stage only feature-owned files in a dirty tree; confirm local HEAD equals the pushed remote branch.

## Common pitfalls

- A regex like `/app/projects/[^/]+` also matches `/app/projects/new`; explicitly reject the `new` sentinel in E2E URL assertions.
- Do not describe the bulk endpoint as transactionally all-or-nothing if successful posts remain scheduled after another post fails.
- COUNT-then-INSERT admission without a schema constraint races across requests/instances.
- Startup migration is not a worker recovery mechanism; recovery must be lease/age based.
- Generated file garbage collection and project-list N+1 optimization are follow-up concerns, not reasons to weaken correctness or broaden the initial delivery.
