# Scoped Role Assignment Modal Triage

Use when an admin/member-management UI assigns a scoped role (for example product/session manager) via a checklist, and reports that save is blocked, silently changes after reload, or includes nonsensical resources.

## Checks

1. Separate **assignable scope** from generic active resources.
   - Inspect the frontend query/filter feeding the checklist.
   - If the role only applies to sessions/events, do not show simple/redeemable products just because they are `active`.
   - Verify the API DTO includes a discriminator (`type`, `kind`, `scope`) and the UI filters by it.

2. Trace “last responsible user” guards across UI and API.
   - Backend may correctly deny revoking the only manager (`last_product_manager`, `last_owner`, etc.).
   - Frontend should not silently re-add locked IDs on save without explaining why.
   - Prefer disabled checked boxes with helper copy like “Last manager for this session product” and/or block save with a visible message.

3. Check for partial multi-request saves.
   - `Promise.all([...adds, ...removes])` can leave earlier requests committed if a later request fails.
   - On failure, refetch authoritative state or show a clear error and keep the modal open.
   - If all-or-nothing semantics matter, add a backend replacement endpoint/transaction instead of many independent POST/DELETE calls.

4. Verify cancel is purely local.
   - Opening/checking/unchecking/canceling the modal must not call role APIs or mutate persisted state.
   - If reload shows different data after cancel, inspect prior save attempts, optimistic state, and partial successful requests.

## Minimal regression tests

- Checklist excludes ineligible simple products.
- Last-manager scoped item is locked and explained.
- Backend `last_*` error is shown in the modal, not swallowed.
- Failed partial save refetches or preserves accurate state.
- Cancel after edits makes zero API calls and leaves member roles unchanged.
