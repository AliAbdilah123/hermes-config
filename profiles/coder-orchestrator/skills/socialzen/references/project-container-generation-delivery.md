# Project containers with generated media and bulk scheduling

Use this when changing SocialZen from “one Project equals one publishable post” into a container that owns multiple independently scheduled posts.

## Domain boundary

- Add a real `projects` aggregate; keep `posts`, targets, immutable post versions, publication runs, retry, quota, analytics, and the existing queue as the canonical publishing system.
- Link posts to containers with nullable `posts.project_id`; standalone posts remain valid.
- Backfill legacy Project-shaped posts into same-ID containers without changing post, media, target, version, run, analytics, or public-route identities.
- Preserve the old meaning of `project_versions.project_id` and `publication_runs.project_id`: those columns still identify the publishable post, not the new container.
- Enforce project/post same-owner relationships at both API and database boundaries.

## Bulk scheduling contract

- Partial success is acceptable only when explicit: return one result per requested post and state that earlier successes are not rolled back after a later failure.
- Reuse existing preflight, quota reservation, immutable version/run creation, and destination idempotency. Never add a second scheduler.
- Make the public bulk request replay-safe. Require a validated client idempotency key, persist request hash plus exact completed response under project/user/key, return the same response for identical replay, and reject same-key/different-payload reuse with 409.
- Concurrent same-key submissions must converge on one persisted response and one publication run.
- The frontend must retain one stable key for a payload across network retries. Rotate only after a confirmed response; a changed payload gets a different key, and reverting to an unconfirmed prior payload reuses its prior key.

## Generation boundary

- If no provider exists, production must fail closed with an unavailable response. Never silently report local placeholders as AI output.
- Restrict mock generation to development/test and label outputs clearly in the UI.
- Persist jobs and items with queued/generating/completed/failed states; preserve successful items when retrying failures.
- Enforce one active job per project with a database constraint or serialized durable admission—not `COUNT` followed by `INSERT` alone.
- Multi-instance workers require durable leases: atomically claim queued or expired work, record owner/expiry, renew while processing, and recover only after lease expiry. Startup/schema migration must not unconditionally fail live generating jobs.
- Validate provider output before storage: bounded response/media size, allowed MIME, decoded image dimensions/content, and probed video structure. Sanitize provider errors and keep credentials server-side.
- Generated files need an eventual lifecycle/garbage-collection policy; record this as postponed scope if deletion is not part of the current release.

## TDD and review gates

Write failing tests first for:

1. migration preservation and idempotent legacy backfill;
2. cross-owner linking rejection;
3. multiple child drafts and standalone-post compatibility;
4. partial bulk results plus identical replay, key conflict, and concurrent replay;
5. concurrent generation admission and single worker claim;
6. non-expired leases surviving startup/migration and expired lease recovery;
7. provider fail-closed behavior, mock-only labeling, partial generation failure, and failed-item retry;
8. frontend request-key lifecycle, loading/error/empty states, asset selection, child editing, and separate schedules.

Run focused backend/frontend tests, typecheck, build, and `git diff --check`. Treat unrelated full-suite failures as baseline candidates only after reproducing them independently; do not hide them.

## Deployment proof

- Back up the live binary and database before a migration-bearing restart.
- Deploy the exact verified backend binary and clean frontend `dist/`, restart the service, inspect startup logs, and verify the live schema.
- Probe an authenticated API boundary where possible; an unauthenticated 401 proves routing/security only, not the feature workflow.
- Verify the exact public lazy-loaded workspace chunk and MIME type, not only the homepage.
- Do not mark READY until authenticated public E2E creates a container, adds multiple posts, exercises generation availability/fail-closed behavior, schedules independent posts, and verifies state after reload.
- Keep WORKING/VERIFYING labels while active. Final delivery includes public link, commit, and push evidence.
