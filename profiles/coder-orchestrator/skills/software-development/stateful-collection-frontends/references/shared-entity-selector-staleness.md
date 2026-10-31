# Shared entity selector staleness after CRUD

Use when an entity is successfully created or edited on a management page but a global selector or navigation control remains stale.

## Root-cause trace

1. Identify the selector's actual source, not merely the CRUD endpoint. A common split is:
   - management page: API-backed local component state;
   - global selector: hardcoded seed data, bootstrap data, or a separate store slice.
2. Confirm the mutation succeeds and the management list refreshes.
3. Check whether refresh updates only page-local state. If so, it cannot rerender the global selector.
4. Search for static fixture imports in runtime UI (`mockData`, `seed*`, constants) before changing the API.

## Minimal durable fix

- Put the authoritative entity list in the existing shared application store.
- Expose one shared reload/invalidate function.
- Make both the global selector and management page consume the same list.
- After create/edit/enable/disable, call the shared reload function.
- Preserve authorization: fetch a global list only for users allowed to read it; scoped users retain their authorized subset.

Avoid event buses, duplicated caches, or full-page reloads when a shared store already exists.

## Regression checks

1. Start as an authorized global administrator.
2. Create an entity through the real modal/form.
3. Assert it appears in the global selector without navigation or refresh.
4. Reload the application and assert it remains, proving persistence rather than optimistic-only state.
5. Verify scoped users still see only authorized entities.

For public E2E, do not hardcode selector labels from seed fixtures once entities are mutable. Fetch the authorized live entity list in the authenticated browser context and compare selector options against that response. Stable seeded IDs may still drive workflows that explicitly depend on seeded operational data.
