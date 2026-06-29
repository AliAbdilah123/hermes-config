# Local Go + Vite Kanban status mutation

Use this when a local Go + SQLite + React/Vite project has a Kanban board that can create/list tasks but cannot move cards between columns.

## Pattern

1. Add a task-detail route before more-specific nested task routes are shadowed incorrectly:
   - Keep collection route: `/{tenantID}/tasks` for `GET`/`POST`.
   - Add detail route: `/{tenantID}/tasks/{taskID}` for `PATCH`.
   - Keep nested routes such as `/{tenantID}/tasks/{taskID}/messages` explicitly routed.
2. Backend `PATCH` should:
   - Re-run tenant authorization against the authenticated session.
   - Parse `taskID` and validate the task belongs to `tenantID` in the `UPDATE ... WHERE id=? AND tenant_id=?` predicate.
   - Normalize legacy/internal status aliases if needed (`in_progress` -> `in-progress`, `completed` -> `done`).
   - Reject unknown statuses with a controlled `400 invalid_status` rather than silently writing arbitrary board columns.
   - Return the updated task DTO from the same list/read mapping used by the workspace response.
3. Frontend card controls should:
   - Render status buttons per card for the canonical board statuses.
   - Disable/highlight the current status.
   - `PATCH` the task detail endpoint and merge the returned task into local workspace state.
   - Verify the card visibly moves columns; tests may need to query the page after React re-renders rather than keep using a stale `closest('article')` handle.
4. Tests:
   - Backend: create a task, patch it to another valid status, assert the returned status; patch an invalid status and assert `400 invalid_status`.
   - Frontend: mock the PATCH endpoint, click a status action, then assert the moved status/card is visible after re-render.
5. Deployment/public smoke:
   - Build backend and frontend.
   - Restart the API service, deploy Vite assets, and verify public index + referenced JS/CSS + health endpoint.
   - Run a public authenticated smoke: login, create a task, patch its status, and assert the returned status.

## Pitfalls

- Do not ignore `QueryContext` errors in helper readers that may be called after a write; `rows` can be nil and panic on `rows.Next()` or `rows.Close()`. Return an empty slice or controlled error if the query fails.
- For Vite bundles, verify feature markers in the deployed JS/CSS bundle rather than expecting UI text in `index.html`.
- If the browser-level tool times out on a deployed SPA, use curl/API-level smoke plus asset marker checks as fallback evidence, not as a claim that the browser UI was visually inspected.
