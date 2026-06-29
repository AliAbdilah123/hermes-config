# Local JSON-state API user scoping pitfalls

Use when a migrated local Go/SQLite app stores all application entities in a single JSON `app_state` payload and later adds first-party auth.

## Durable pattern

When adding local auth to a previously demo-user app:

1. Derive `userID` at each request boundary from the bearer/session token; fall back to the demo user only for unauthenticated/demo compatibility.
2. Scope **every read path** and **every graph/summary path**, not just CRUD collection endpoints.
   - Easy miss: `/api/focus` list may use `scopeItems(...)`, while `/api/focus/graph` still calls `focusGraph(st)` on the full state and leaks seeded/other-user plans.
   - Similar risks: dashboards, counts, analytics summaries, calendar aggregations, subtask-count endpoints, focus/energy graphs.
3. New items must be stamped with the signed-in `userId` in a shared constructor such as `newItem(name, body, userID)`.
4. Mutations and deletes should find by both `id` and `userId` (`findOwned`) so one user cannot edit/delete another user's objects.
5. For pre-auth seeded/demo records, keep them under `demoUserID`; authenticated users should not see them unless the product explicitly imports them.

## Regression test recipe

Create two users via the public/local auth endpoints, each with a unique marker entity, then assert each user's list/graph/summary contains only their marker and excludes:
- the other user's marker
- seeded/demo marker data

For graph endpoints, test the graph response directly, not just the underlying list endpoint. A passing list test does not prove the aggregate is scoped.

Example assertions:
- User A focus graph contains `OnlyA`
- User A focus graph excludes `OnlyB`
- User A focus graph excludes seeded `Deep work`
- User B mirrors the same isolation

## Deployment verification

After `go test ./...`, rebuild/restart the Go service and run a public smoke test through nginx using two newly-created users. Avoid printing tokens in logs or final summaries; report booleans such as `user_a_graph_excludes_user_b_focus: true`.