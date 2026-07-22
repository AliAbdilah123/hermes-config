# Clean artifact deployment from a dirty worktree

Use when a shared repository contains unrelated tracked or untracked changes while a focused frontend feature must be deployed.

## Risk

Selective `git add` and a scoped commit protect commit history, but they do not isolate the build. A normal `npm run build` compiles the entire current working tree, including unrelated uncommitted source edits. Copying that output to production can silently deploy work that was intentionally excluded from the commit.

## Safe workflow

1. Commit only the task files and verify the commit diff.
2. Create a temporary clean worktree at that commit, preferably outside the repository:
   `git worktree add --detach /tmp/project-deploy-<sha> <sha>`
3. Install or reuse dependencies according to the repository's lockfile policy. Never copy dirty source into the worktree.
4. Run changed-feature tests, lint, and the production build in the clean worktree.
5. Deploy only that clean worktree's build output.
6. Verify the live HTML references the expected asset hashes and exercise the cache-busted public route at the acceptance viewport.
7. Remove the temporary worktree:
   `git worktree remove /tmp/project-deploy-<sha>`

If dependency installation is expensive, a project-approved shared package cache is fine; source and generated output must still originate from the clean commit checkout.

## Acceptance

- `HEAD` equals the pushed upstream SHA.
- The deployed artifact was built from that SHA without unrelated working-tree edits.
- Live HTML serves the expected new asset hashes.
- Browser QA confirms the requested viewport behavior and no desktop regression.
