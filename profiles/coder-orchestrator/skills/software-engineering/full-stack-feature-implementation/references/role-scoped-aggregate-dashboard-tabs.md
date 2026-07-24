# Role-scoped aggregate dashboard tabs

Use this pattern when simplifying a role-specific dashboard into a small set of functional tabs while one tab needs an aggregate over records owned by the signed-in actor.

## Minimal implementation sequence

1. Trace every navigation surface: canonical routes, legacy redirects, sidebar/workspace navigation, the visible tab strip, and route tests.
2. Redirect the role workspace index to the first retained functional tab instead of preserving an empty overview.
3. Reuse the existing feature view in its new tab; do not duplicate a table that already owns loading, filtering, and role behavior.
4. Enforce actor scoping on the server. Resolve the authorized actor's domain membership ID, then aggregate only records assigned to it.
5. Define attendance semantics explicitly in SQL: include present records; exclude cancelled claims and cancelled sessions; group by member; sort count descending with deterministic name/email/ID tie-breakers.
6. Return a narrow aggregate DTO rather than stretching an unrelated dashboard-summary response.

## Verification ladder

- Add a backend test proving actor ownership, cancellation exclusions, grouping, and descending frequency.
- Add a frontend test proving rows render in API order and navigation exposes exactly the retained tabs.
- Run focused backend and frontend tests first, then the production build.
- Run the broader suite when practical. If it fails outside the touched scope, rerun focused tests and report the unrelated failure precisely; do not repair unrelated dirty work without authorization.

## Dirty-worktree discipline

Record `git status` before editing. Stage only explicit feature files. Inspect the staged diff and run `git diff --cached --check` before committing so pre-existing modifications are neither overwritten nor accidentally shipped.
