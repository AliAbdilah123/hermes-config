# Clean-build deployment gate

Use when an approved UI change is committed from a dirty repository and the working-tree build passes.

## Rule

A successful dirty-workspace build is not deployable evidence. Build the committed SHA in a clean worktree before release because the dirty build may contain unrelated prerequisites or uncommitted fixes.

If the clean build fails:

1. Stop before `rsync`, upload, restart, or any other release action.
2. Leave the currently deployed public assets unchanged.
3. Identify the exact unrelated compile/test boundary.
4. Either commit only genuinely required prerequisites after focused review, or revise the feature so HEAD builds independently.
5. Keep the ship/deploy task blocked; do not mark it complete.
6. Do not copy or `rsync` a previously generated dirty-workspace `dist/` after this failure. Bundle markers only prove that dirty artifact contains the feature; they do not establish commit provenance.
7. Report “committed and pushed; deployment blocked,” never “implemented and deployed.”

Passing focused tests, bundle-string checks, HTTP 200, and matching public/local asset hashes do not prove the new commit was deployed. Deployment proof requires assets built from the clean commit and verified at the public route. Run the clean-build gate before any command capable of changing production.