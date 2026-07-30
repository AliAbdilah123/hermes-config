# Role-Scoped Session Operations in Functional Previews

Use this pattern when a role-specific dashboard reuses an administrator's session-operation components.

## Adapt capabilities, not components

Reuse the shared controller, occurrence model, rows, calendar, attendance panel, and deactivation dialog. Keep the API authoritative.

- Admin: program-wide scope, assignment/reassignment, all authorized session operations.
- Product manager: assigned product only, self-activation, attendance/deactivation only for owned active sessions.
- Foreign-owned sessions: visible but locked/read-only.
- Reassignment: Admin-only.

Preserve structural layout invariants when adding locks/statuses; for grid rows, regression-test the expected direct-child count.

## Mutation contract

Never launch an operational mutation from an unawaited inline async shortcut. The shared view must set busy state, await generation/mutation/refresh, announce success, display API failures in an alert, and restore actions after failure.

## Dual-role pitfall

A caller can be both Admin and Product Manager. If self-activation omits `managerId`, an API that branches on `isAdmin` first may return `manager_required` rather than derive the caller's product-manager membership.

Activation rules:

- Explicit Admin `managerId` preserves assignment semantics.
- Empty `managerId` derives the caller's active product-manager membership when present, even for dual-role callers.
- A manager-supplied conflicting ID cannot override self-assignment.
- Reassignment remains forbidden to manager-only callers.

Add a dual-role regression; manager-only tests do not cover branch ambiguity.

## Public proof

A page render, HTTP 200, build, or unit test is insufficient. Against an isolated preview API/database, authenticate as the named role and exercise:

1. Activate an inactive occurrence.
2. Assert active state and ownership.
3. Open attendance and verify loaded/empty content.
4. Deactivate with a reason.
5. Assert inactive/cancelled state and cleared ownership.
6. Assert foreign-owned rows expose no mutations.
7. Fail on unexpected API 4xx/5xx.
8. Inspect final screenshot and database state.

Reset only the isolated preview fixture before rerunning destructive E2E. An already-active fixture is test-state contamination, not necessarily an app regression.
