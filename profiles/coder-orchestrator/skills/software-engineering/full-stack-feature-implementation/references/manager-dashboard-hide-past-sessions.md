# Manager dashboard: hide past sessions without losing access

Use this when a manager/operator dashboard lists recent sessions and the page becomes crowded because past sessions dominate the schedule list.

## Pattern

- Keep current/future operational sessions visible by default.
- Hide `day_group === 'past'` (or equivalent historical groups) behind a compact full-width toggle such as `Show N past sessions` / `Hide past sessions`.
- Preserve access to past sessions instead of deleting them from the query or moving them out of reach; managers may still need history for attendance, deactivation reasons, and audit review.
- Update the section summary to make the hidden state explicit, e.g. `4 shown · 3 past hidden · Today · Tomorrow`.
- When rendering day dividers from a filtered list, compute dividers from the visible list so the hidden `Past` divider does not leave empty clutter.

## Test updates

- Existing tests that indexed into an all-session array often need remapping after past sessions are hidden; the first visible card may shift from index 3 to index 0.
- Add tests for both default-hidden behavior and reveal-on-demand behavior.
- For tests that assert properties of past sessions, click the reveal toggle before querying past cards.
- Keep current-session action tests against visible current/future cards; do not reveal past sessions unnecessarily.

## Verification

1. Run the targeted dashboard/component test file.
2. Run the frontend production build.
3. Deploy the built assets and verify the deployed bundle contains the new toggle text (`Show ... past sessions` or `Hide past sessions`).
