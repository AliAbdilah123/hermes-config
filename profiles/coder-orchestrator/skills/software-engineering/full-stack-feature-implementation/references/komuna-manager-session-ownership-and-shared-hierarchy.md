# Komuna manager session ownership and shared hierarchy

Use when giving product managers Admin-Sessions-like controls while scoping them to one managed product.

## Product hierarchy and reuse

- Reuse a real shared presentation seam between admin and manager views; visual similarity or continued use of a separate legacy manager card does not satisfy cross-role reuse.
- A small shared `ProductSessionHierarchy`-style wrapper is often enough: dominant product header, left chevron, compact subordinate rows, maximum five upcoming sessions, and a `See detail` footer.
- Keep role-specific row behavior injectable. Admin retains manager selection/reassignment; manager mode has no picker and preserves manager-specific claims, QR, attendance, and alias behavior.
- Never expose user-facing `Template` wording. Internal template API/model names may remain.
- Preserve the host manager dashboard's metrics and approvals; replace only its sessions surface.

## Ownership model

- For manager activation, derive the active product-manager membership server-side. Never trust a body-supplied manager ID.
- Claim atomically with a conditional update and check `RowsAffected == 1`; return `409 Conflict` to the loser rather than overwriting ownership.
- Admin activation/reassignment remains an explicit override path but must still check update results and audit transactionally.
- Managers may deactivate only sessions assigned to them. Clear `assigned_manager_id` and display coach in the same cancellation transaction.
- A released cancelled session must be claimable again. Activation predicates therefore need to allow the intentional cancelled+unassigned state while still blocking completed, ended, attendance-recorded, or assigned sessions.
- Session-list DTOs must serialize both the assigned membership ID and its user ID (for example `managerUserId`). The frontend cannot recognize its own ownership if only the membership ID/name is returned; it will misclassify every owned row as foreign and hide valid controls.
- Foreign-owned sessions remain visible and read-only. Use exact explanatory copy when specified, such as: `Only the assigned manager or an administrator can deactivate this session.`

## Mutation safety beyond activation

Ownership protection must cover every mutation surfaced by the expanded session row, not just activate/deactivate:

- Attendance lookup must be scoped by both `claim_id` and `session_id`.
- Claim alias mutation requires method enforcement, authentication, and admin-or-owning-manager authorization through claim → session → product/program.
- Attendance/alias updates must check SQL errors and affected-row counts; never return success or write audit for a nonexistent or cross-session claim.
- Cancellation/refund transactions must check every scan/query/insert/update and preserve the first error. Ignoring an intermediate claim or voucher failure can commit a cancelled session with incomplete refunds.
- Keep state mutation and audit in the same transaction whenever the audit claims that mutation occurred.

## TDD and review checklist

Write failing tests first for:

1. Server-derived self-claim and rejection of body-selected manager.
2. Exactly one concurrent claim winner.
3. Foreign-owner activation, deactivation, attendance, and alias denial.
4. Owner deactivation clears assignment.
5. Cancelled+released session can be reclaimed.
6. Completed/ended/attendance-recorded sessions remain locked.
7. Admin override remains functional.
8. Session list returns `managerUserId` and frontend recognizes own ownership.
9. Shared hierarchy is rendered by both admin and manager surfaces.
10. Product title dominance, compact rows, left icon, max five, `See detail`, and absence of user-facing `Template`.

Before deployment, use an independent reviewer specifically for authorization, transaction rollback, DTO ownership fields, reactivation state predicates, and whether the promised shared component is actually imported by both role surfaces. Focused tests and a successful build can still miss all five classes of defect.
