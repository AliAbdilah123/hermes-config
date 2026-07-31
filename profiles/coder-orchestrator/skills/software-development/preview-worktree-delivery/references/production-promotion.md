# Production promotion from a long-lived preview branch

## Checklist

1. Fetch remotes and inspect both the production checkout and preview worktree.
2. If production is dirty or stale, leave it untouched. Create a clean integration worktree from current `origin/master`.
3. List `origin/master..preview-branch` and identify the exact approved commit range. Exclude unrelated earlier preview commits.
4. Cherry-pick or squash only that range. If conflicts arise:
   - Compare stage 2 (current production) and stage 3 (preview change).
   - Preserve newer production behavior and layer only the approved capability onto it.
   - Reconcile DTO/model shapes explicitly; do not assume preview-era response fields still match current production.
5. Run focused authorization/migration tests, UI regressions, lint, build, and `git diff --check` on the integrated tree.
6. Commit and push the exact verified integration state before deploying.
7. Build the API from the integration tree; replace the server artifact atomically and verify service health.
8. Deploy the frontend from a clean `dist/`, preserving runtime paths such as uploads. Confirm the public page references the new asset hash.
9. Run authenticated public E2E on production. Verify both data visibility and authorization. Prefer non-mutating existing records; only exercise production mutations when necessary and safe.
10. Report the production URL, final pushed commit, deployment status, and exact public E2E evidence.

## Common reconciliation trap

A preview branch may include a DTO field such as a single selected product name while current production already models a list of selectable Simple products. Keep the current class-level model and adapt tests/UI to it rather than reintroducing the obsolete preview representation.
