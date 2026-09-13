# Configurable persisted options: verification matrix

Use this matrix when replacing hard-coded workflow choices with admin-managed persisted records such as order types, fulfillment modes, statuses, or categories.

## Strict RED sequence

Write and run one behavioral test before each production change:

1. **Seed/migration:** legacy storage without the collection receives defaults; historical free-form labels still render.
2. **Validation:** trim at the trust boundary; reject blank and case-insensitive duplicate names.
3. **Lifecycle:** add, enable/disable, and archive. Archive referenced records rather than deleting them.
4. **Consumer filtering:** only enabled, non-archived records appear in creation flows.
5. **Selection repair:** when the selected record becomes unavailable, choose the first available record deterministically.
6. **Empty state:** no available records produces an explicit state and disables submission.
7. **Behavior flags:** conditional UI and persisted fields come from record metadata (for example `requiresTable`), never display-name comparisons.
8. **History:** archived configuration must not erase immutable labels already stored on historical transactions.

## Harness pitfalls

- Scope repeated registry-row assertions with `within(row)`; metadata and action labels often repeat.
- Responsive UIs may render duplicate controls. Assert every copy has the required state rather than using a singular query.
- In TypeScript, use `closest<HTMLElement>(selector)` before passing a row to `within`; runtime tests can pass while test source fails typecheck.
- A valid RED failure must come from missing behavior, not a missing route, ambiguous query, typo, or test compile error.

## Completion gate

After focused RED→GREEN, run full tests, lint, typecheck, and production build from the package root. A green runtime suite does not prove that test source typechecks.