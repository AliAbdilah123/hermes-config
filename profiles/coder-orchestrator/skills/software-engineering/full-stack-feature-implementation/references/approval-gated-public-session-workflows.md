# Approval-gated public session workflows

Use this pattern for table ordering and similar guest submissions that must be reviewed by authenticated operators.

## Boundary and lifecycle
- Treat the guest submission as an approval request, not the canonical domain record.
- Bind expiring sessions to tenant/location, resource (for example table), creator, creation, and expiry. Default to one active session per resource.
- Keep the guest route outside the authenticated application provider/shell: no login flash, staff navigation, or cached staff state.
- Guest submission must not reserve stock, mutate inventory, take payment, or enter fulfillment.
- Persist stable client/idempotency keys. Prefer a unique database constraint; document best-effort dedupe ceilings explicitly.
- Rejection requires reason, actor, and timestamp.
- Approval re-reads current canonical data and recomputes price/availability. In one write transaction, verify pending state, create/append the canonical record, and resolve the request so concurrent approvals cannot duplicate work.

## Printable QR
Build the QR from a root/subpath-safe public URL. Print-only output includes brand/tenant, resource label, instruction, and expiry. Verify the button invokes `window.print`; `@media print` must hide the application shell and expose only the card.

## Debugging pitfalls
Avoid naming a selected row the same as a row-mapping helper; shadowing can surface only in the approval branch. Generic HTTP error masking may then hide the original exception. Preserve the original error, and make rollback tolerant if a branch may already have rolled back.

## Public E2E
Use separate staff and guest browser pages:
1. Staff creates session and opens QR/share dialog.
2. Assert print invocation.
3. Guest opens the public URL at mobile width and has no staff shell/sidebar.
4. Guest adds and submits, reaching the exact pending state.
5. Staff approves; guest polling reaches approved.
6. Close test sessions afterward so one-active-session guards do not poison reruns.

Filter an expected unauthenticated session-probe 401 only by exact scope; never suppress unrelated browser errors.
