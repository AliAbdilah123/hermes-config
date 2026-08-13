# Mutation Refresh Contract Verification

Use when reducing frontend refetches after CRUD, status, reorder, or relationship mutations.

## Model the affected datasets first

Name each mounted projection separately, for example:

- task-list query
- visible-date goals containing embedded tasks and counts
- filtered goals page
- expanded-subtask cache
- picker data loaded on dialog open

A mutation should update only projections it can affect. Do not treat every GET observed near a mutation as mutation-triggered; capture request timestamps and call ordering to distinguish save callbacks from initial loading, dialog-open picker requests, polling, date-range effects, and rerenders.

## Preferred update rules

- Ordinary create/edit/status: patch the returned entity into mounted state.
- Create that introduces an unknown container (for example, an auto-created daily goal): refetch only that visible/filtered container query.
- Relationship or hierarchy changes: invalidate only affected old/new parents when possible.
- Reorder: keep optimistic order on success; refetch only as failure recovery.
- Filter-membership changes (status/date/category): a scoped list refetch is acceptable when local membership logic would duplicate server rules.
- Await async mutation callbacks so request ordering and modal completion are deterministic.

## Browser request-count proof

For every optimized path:

1. Authenticate through the exact public app.
2. Wait for initial route/dialog requests to settle.
3. Record the relevant GET counter immediately before the mutation.
4. Perform the mutation and wait for its POST/PUT/DELETE response.
5. Assert the UI changed correctly.
6. Wait a bounded interval and assert the relevant GET delta.
7. Capture the exact request timeline, console errors, and a screenshot.

Minimum matrix:

- ordinary create into an existing visible container: expected scoped-container GET delta `0`
- create that auto-creates an unknown visible container: expected scoped-container GET delta `>=1` (normally exactly `1`, unless documented lifecycle requests exist)
- status toggle: expected list GET delta `0`
- successful reorder: expected list/container GET delta `0`
- failed optimistic mutation: expected recovery refetch and restored authoritative state

## Completion gate

Do not call the optimization READY merely because one path has zero refetches. If a sibling path still exceeds its intended request budget, keep status WORKING and trace that request to its source before another edit. Report separate request counts for route-open, dialog-open, mutation, and post-mutation windows.

## Test hygiene

Request-count tests should block the mutation response briefly when useful; this exposes premature refetch races. Ensure tests count only the exact endpoint and HTTP method. Restore generated Playwright reports and lockfile churn that were clean before the run; stage explicit product/test paths only.
