# Job-detail archive action

Use when adding an Archive action to an existing job-detail UI whose active board has no archive model yet.

## Minimal product model

If restoration or an archived-jobs browser is not requested, treat archive as removal from the active board rather than adding a speculative `archived_at` field/state. Restrict it to terminal jobs (for example, `done`) so active scheduler/session state cannot be destroyed.

- Add `DELETE /api/jobs/{id}` to the existing authenticated job-detail route.
- Resolve the job with the authenticated owner scope first; preserve `404` for cross-user access.
- Return `409` for non-terminal jobs.
- Return `204` after deletion and signal the existing board refresh/SSE mechanism.
- In the detail modal, show Archive only in the terminal state and reuse the existing refresh + close behavior.
- Do not add a dependency, confirmation state machine, schema migration, or archived listing unless explicitly requested.

## Deletion reliability with SQLite

Do not assume declared `ON DELETE CASCADE` proves runtime cascading. SQLite foreign-key enforcement is connection-local; a startup `PRAGMA foreign_keys=ON` may not cover every connection in a pooled `database/sql` handle.

For a small app, the shortest reliable archive path is one transaction that explicitly deletes dependent event rows, then run rows, then the owned job row. If the application already guarantees foreign keys on every connection, direct parent deletion is acceptable—but prove cascade behavior with a real test.

## Focused TDD check

Before implementation, add one API test that verifies:

1. deleting a non-terminal job returns `409`;
2. another user receives `404`;
3. deleting the owner's terminal job returns `204`;
4. the job, runs, and events are all gone.

Insert a real run and event fixture. Check every fixture insert error so a missing required column cannot turn the test into a nil-result panic.

## Delivery checks

Run backend tests, frontend tests, and the production build. Verify the deployed bundle contains the Archive label and the running service is healthy. Keep unrelated pre-existing working-tree changes unstaged. If no Git remote exists, commit locally and report push as blocked rather than inventing success.
