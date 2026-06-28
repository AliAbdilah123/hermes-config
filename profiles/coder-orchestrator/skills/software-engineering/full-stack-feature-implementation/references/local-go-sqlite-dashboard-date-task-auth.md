# Local Go + SQLite dashboard date-task and auth migration notes

Use when a migrated React/Vite app has a local Go + SQLite backend and users report that auth or dashboard date task creation does not work.

## Durable debugging pattern

1. **Auth parity check**
   - Inspect the frontend auth context and sign-in/sign-up routes. A hardcoded user, "demo session active" page, no-op `signOut`, or a constant token means auth is still a demo shim.
   - Inspect Go `/api/auth/*` routes. A catch-all route returning a demo user for every auth path is not functional auth.
   - Add first-party local auth when cloud auth has been removed: sign-up, sign-in, sign-out, and `/auth/me` backed by persisted users/sessions.
   - Frontend should store the local session token, set the API client's token getter, load `/auth/me` on startup, and expose real sign-in/sign-up forms.

2. **Create task for selected date**
   - Trace from dashboard `TaskDialog` props through API client to the backend route. Watch for frontend code that drops `goalId` when `createForDate` is set.
   - Backend `/tasks/date/:date` should not just stamp a `date` field. It should:
     - preserve an explicit `goalId` if supplied;
     - otherwise find the active `Daily` goal whose date range contains the selected date;
     - if none exists, create an active `Daily` goal for that date;
     - attach the new task and any new/existing subtasks to that goal.

3. **Payload parity gaps to audit**
   - Migrated frontends often send batch payloads that a simple local Go shim ignores: `newSubtasks`, `existingSubtaskIds`, goal `newTasks`, `existingTaskIds`, and `selectedTaskIds`.
   - Implement these in local handlers before trusting dashboard/goal dialogs.
   - Goal list endpoints used by dashboards usually need `status`, `startDate`, `endDate`, and `alwaysIncludeMainGoals` filtering semantics, not just search/limit/offset.

## Regression tests to add

- `POST /api/auth/sign-up` returns a user and token; `GET /api/auth/me` with the bearer token returns that user.
- `POST /api/tasks/date/<future-date>` with no goal creates/links a Daily goal for that exact date.
- `GET /api/goals?status=active&startDate=<date>&endDate=<date>&alwaysIncludeMainGoals=true` returns that goal with `taskCount >= 1`.

## Public smoke test shape

After deployment, smoke through the public subpath/proxy, not only localhost:

- `/projects/<slug>/api/healthz`
- sign-up with a unique throwaway email
- `/auth/me` with the returned bearer token
- create a dated task for a far-future date
- query goals for that date and confirm the linked Daily goal appears
- clean up the smoke task/goal

Do not print auth tokens in logs or summaries; keep them in script variables only.
