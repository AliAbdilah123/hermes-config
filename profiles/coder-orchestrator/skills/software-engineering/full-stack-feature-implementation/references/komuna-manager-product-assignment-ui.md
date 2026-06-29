# Komuna manager product assignment UI

Use when implementing product-scoped manager assignment in Komuna's `apps/web` members admin UI.

## Durable pattern

- The existing API already supports product-scoped manager roles via `POST /programs/:programId/members/:userId/roles` and `DELETE /programs/:programId/members/:userId/roles` with `{ role: 'manager', productId }`.
- Frontend should fetch active products from `/programs/:programId/products` and hide archived products in the assignment modal.
- Preserve member role display as de-duplicated role names, but keep separate `managedProductIds` derived from `MemberDTO.roles` entries where `role === 'manager' && product_id`.
- Add both global and row-level entry points:
  - Global Add Manager: pick an existing active member and active products.
  - Row action: edit a member's managed products.
- Saving should diff selected product IDs against existing product IDs and only call role add/remove endpoints for changes.
- If the resulting product set is empty, remove the local `manager` role display so the row reflects no managed products.
- Show managed product chips on member rows by mapping `managedProductIds` to active product names.

## Test pattern

In `apps/web/src/__tests__/MembersPage.test.tsx`:
- Extend mocked `apiClient.get` to return `/programs/p1/products`.
- Test the global workflow calls `apiClient.post('/programs/p1/members/:userId/roles', { role: 'manager', productId })`.
- Assert archived products are absent from the modal.
- Test row-level edit removes a product by calling `apiClient.del(..., { role: 'manager', productId })` and removes manager/product chips locally.

## Branch/update pitfall

When a plan file is pulled from a remote branch and the branch is behind by exactly that plan commit, do not leave a manually checked-out `.omo/plans/*` file staged and then commit on the stale local branch. First fast-forward the branch (`git pull --ff-only origin <branch>`) so the remote plan commit is incorporated, then commit implementation changes on top. If the plan file was manually staged, unstage/remove the local copy before the fast-forward to avoid duplicate/conflict noise.