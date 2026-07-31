---
name: role-scoped-dashboard-operations
description: Reuse privileged admin operational dashboards for narrower manager/operator roles while preserving server-side scope, ownership, lifecycle rules, and public E2E verification.
version: 1.0.0
metadata:
  hermes:
    tags: [dashboards, authorization, role-scope, operations, verification]
---

# Role-Scoped Dashboard Operations

Use when an admin dashboard already has working operational mechanics and a manager/operator dashboard should reuse them with narrower permissions.

## Principle

Reuse the admin controller and operational components rather than creating a second implementation. Adapt behavior through a small explicit capability policy at the shared view boundary. The API remains the authorization boundary; frontend capability flags explain and constrain UX but never grant authority.

## Workflow

1. Inventory the admin operation end to end: shared view, controller/hook, API client method, route/handler, database mutation, lifecycle checks, and tests.
2. Compare the narrower role's resource scope and ownership rules operation by operation.
3. Reuse shared rows, dialogs, calendars, attendance/detail panels, mapping functions, and mutation methods.
4. Express differences as explicit capabilities such as `canActivate`, `canReassign`, `canViewAttendance`, and `canDeactivate`; avoid scattered `mode === 'manager'` branches.
5. Ensure every mutation is awaited and has busy, success, visible error, refresh, and duplicate-click prevention.
6. Enforce scope and ownership atomically in the backend. Never rely on hidden buttons.
7. Add frontend and backend regressions for own, foreign-owned, inactive-role, terminal-state, and privileged-admin cases.
8. Verify through a data-backed public preview as the named role, performing real mutations—not merely loading the page.

## Capability adaptation pattern

Typical session operations:

| Operation | Admin | Scoped manager |
|---|---|---|
| Resource scope | All resources in tenant/program | Assigned resource only |
| Activate | Choose eligible assignee | Confirm self-assignment |
| Reassign | Allowed | Hidden and API-forbidden |
| Attendance/details | Any active owned resource | Own active resource only |
| Deactivate | Lifecycle rules | Own resource plus lifecycle rules |
| Foreign-owned row | Operational | Locked/read-only |
| History | Tenant/program-wide | Assigned resource only |

## Dead-control pitfall

A button can render correctly yet be nonfunctional when a role-specific shortcut launches an inline unawaited async closure. Symptoms include no busy state, swallowed errors, missing refresh, repeated clicks, and incomplete assignment data.

Use one awaited controller action. If an occurrence/resource must first be generated: generate it, perform the server-authorized mutation, refresh authoritative data, and announce success. On failure, restore controls and show a retryable alert.

## Display identity versus authority

A scoped page may intentionally omit a broad member/user directory. When authoritative occurrence DTOs already contain assignee identity, use lookup data when available and fall back to occurrence fields for display. Do not broaden data access solely to render a name. Ownership decisions must still use authenticated IDs and server-side predicates.

Treat profile images as an end-to-end DTO path, not a component-only change:

1. Join the authoritative profile image field in the scoped API query.
2. Convert stored extensions/paths through the existing server URL helper.
3. Add the field to the TypeScript DTO and occurrence/member view model.
4. Render it in every shared surface: compact row, calendar/detail panel, attendee panel, and hydrated selections where applicable.
5. Pass returned paths through the preview-aware asset URL helper and retain initials plus failed-image fallback.
6. Publicly verify a profile path known to exist returns `200` with an image MIME type.

Do not infer filenames or fetch a broad user directory just to obtain avatars.

## Dual-role actors

A user can hold both Admin and scoped-manager roles. Avoid unconditional “Admin first” branching when the narrower UI intentionally sends manager semantics, such as activation without an explicit assignee. Otherwise the API may demand an Admin-only picker value and break manager self-assignment.

For operations with omitted assignee identity:

- first determine whether the actor is an active manager for the target resource;
- derive self-assignment when that narrower relationship exists, even if the actor is also Admin;
- preserve explicit Admin assignment/reassignment behavior when an assignee ID is supplied;
- add a dedicated dual-role regression—single-role tests will not expose this bug.

## Read paths need authorization too

Detail endpoints such as `/sessions/:id/claims` are authorization boundaries, not harmless display helpers. Apply the same tenant, product, and owner checks used by attendance mutations before returning names, emails, profile pictures, booking details, or claims. Test both the owning manager’s detailed response and a foreign manager’s `403`.

For Admin-parity attendee context, enrich this already-secured claims response with the selected **Simple product** and labeled custom-field answers; do not fetch a broad member/bookings directory or create a parallel manager details API. Keep the values read-only unless editing is explicitly requested, omit empty details, and preserve responsive wrapping in the shared attendance row. See `references/scoped-attendee-booking-details.md` for the data path and regression matrix.

## Legacy database diagnosis

If a deployed or copied runtime database returns a generic DB error while fresh-schema tests pass:

1. Identify the exact query behind the failing tab.
2. Compare every selected/filtered column with `PRAGMA table_info` or the equivalent live schema inspection.
3. Remember that adding columns to `CREATE TABLE IF NOT EXISTS` does not migrate existing tables.
4. Add idempotent `ALTER TABLE ... ADD COLUMN` migrations using the project's existing duplicate-column handling.
5. Add a regression that constructs the legacy table shape, boots the real application migration path, and calls the real failing query.

Do not patch only the copied preview database; fix startup migration so every old database is repaired.

## Regression matrix

Frontend:

- allowed operation succeeds and refreshes;
- busy state prevents duplicate mutation;
- API failure is visible and retryable;
- own resource exposes permitted controls;
- foreign-owned resource is locked and exposes no mutations;
- admin-only reassignment is absent;
- shared layout invariants remain intact when lock/status content changes.

Backend:

- scoped actor can mutate only assigned resources;
- self-assignment is derived server-side;
- supplied foreign assignee IDs cannot escalate authority;
- competing ownership claims conflict atomically;
- owner-only detail/attendance/deactivation checks hold;
- terminal/lifecycle constraints remain enforced;
- admin parity remains unchanged.

## Public verification gate

Tests and builds are necessary but insufficient. Before calling operational dashboard behavior fixed:

1. Use an isolated public preview with a separate API/database.
2. Authenticate as the named manager/operator.
3. Perform a real allowed mutation and verify persisted ownership/state after refresh.
4. Exercise the dependent operational flow (for example attendees and deactivation).
5. Prove a foreign-owned resource remains locked.
6. Inspect failed network responses and console errors.
7. Capture desktop and mobile evidence.

If this exact E2E has not run, report **implemented but not publicly verified**, not **fixed**.

## Review-first boundary

For broad operational redesigns, produce a role matrix and static review artifact before implementation. Clearly label it as static and keep an explicit implementation gate. A review link is not a functional preview link, and approval of the review does not authorize production deployment.
