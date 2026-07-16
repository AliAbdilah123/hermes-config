# Komuna manager-scoped reuse of Admin Sessions

Use when planning or implementing session operations on the product-manager dashboard by reusing the Admin Dashboard Sessions experience.

## Reuse seam

- Admin production path is already separated into `SessionsTab.tsx` → `admin-sessions/useAdminSessions.ts` → `SessionsTabView.tsx`.
- Reuse the admin controller/view-model and prototype presentation suite through a small role/capability policy. Do not build a second parallel sessions UI from the legacy manager `SessionCard` path.
- In manager mode, pass the route product ID as a mandatory scope and preserve the dashboard metrics and Pending Approvals; replace only the minimal Sessions section.
- Admin mode keeps manager selection/reassignment. Manager mode removes those controls and derives the actor server-side.

## Ownership state machine

- Inactive + unassigned: any eligible manager for that product may activate and atomically self-assign.
- Active + owned by actor: actor may deactivate with confirmation.
- Active + owned by another manager: visible but locked; show manager identity and a short ownership explanation.
- Completed/finalized or attendance-recorded: read-only.
- Manager deactivation clears assignment atomically. There is no manager-to-manager takeover; administrators retain override authority.

## Backend requirements

Disabled controls are not authorization. In the Go API:

- Resolve the active product-manager membership from the authenticated actor; never trust a manager ID supplied by the manager client.
- Claim with conditional SQL (`... WHERE id=? AND assigned_manager_id IS NULL`) in a transaction and check `RowsAffected`; return `409 Conflict` for a lost race.
- Release/deactivate with an ownership predicate (`... WHERE id=? AND assigned_manager_id=?`) for manager actors.
- Preserve the existing cancellation/refund semantics if deactivation currently means cancellation, but clear `assigned_manager_id` and display coach fields in the same transaction.
- Keep admin explicit assignment/reassignment as a separate policy branch.
- Validate active membership, lifecycle/attendance locks, HTTP methods, DB errors, and audit writes.

## Plan/design review expectations

When the user requests planning before implementation:

- Inspect both admin and manager implementations plus backend mutation rules before drafting.
- Publish separate plan and static design pages.
- The design must preserve the real manager shell—no invented sidebar—and show at least: unassigned actionable, owned by self, owned by another manager/locked, and finalized/read-only rows.
- Include an explicit implementation gate. Policy answers or design approval are not implementation permission.

## Regression coverage

Backend tests: self-claim, body cannot nominate another manager, exactly one concurrent winner, foreign-owner denial, owner release clears assignment, admin override, inactive membership denial, terminal/attendance lock, controlled error/status responses.

Frontend tests: one-product scope, no picker in manager mode, self-activation, conflict feedback, foreign-owner lock copy, own deactivation, past history, metrics/approvals preservation, and unchanged admin picker behavior.
