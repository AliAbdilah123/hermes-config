---
name: preview-worktree-delivery
description: Preserve and deliver accumulated changes safely in long-lived isolated preview worktrees without confusing preview commits with production approval.
version: 1.0.0
---

# Preview Worktree Delivery

## Use when

Use for multi-revision work performed in an isolated preview worktree, especially when the worktree is dirty, publicly deployed for review, or handed among multiple agents.

## Workflow

1. Record the worktree baseline, branch, status, and whether the user currently forbids commits.
2. Preserve existing dirty changes. Never reset, stash, or overwrite them implicitly.
3. Revalidate inherited constraints whenever the task changes or expands. A handoff constraint such as “do not commit” belongs to the scope that established it; do not silently extend it through unrelated later revisions.
4. After substantial validated work accumulates, explicitly report whether changes are committed. If commit intent is unclear, ask whether the user wants checkpoint commits rather than leaving a large dirty worktree indefinitely.
5. Unless commits are currently forbidden, checkpoint reviewed source changes in logical commits and push the preview branch as backup.
   - Derive groups from behavior boundaries, not arbitrary file counts: for example API/domain rules, preview media resolution, checkout/navigation intent, admin forms, attendee UI, then fixture-only compatibility updates.
   - Stage explicit paths for one group, inspect `git diff --cached --stat` and `git diff --cached`, run `git diff --cached --check`, commit, and repeat. Never use `git add .` in a dirty preview worktree.
   - After all groups, run tests/build from the committed state and confirm `git status --short --branch` contains only intentionally excluded runtime artifacts.
6. Exclude runtime and generated artifacts: databases, uploaded fixtures, built binaries, credentials, environment files, and build output unless the repository intentionally tracks it.
7. A preview-branch commit or push is preservation, not approval to merge, deploy production, or modify production data.
8. After explicit production approval, promote from a clean integration worktree based on current `origin/master`; never merge, build, or deploy from a dirty/stale production checkout.
   - Fetch first and compare the preview branch to current production.
   - Select only the approved feature commit range. Do not carry older unrelated preview work merely because it shares the branch.
   - Prefer a clean cherry-pick/squash integration. When production evolved independently, reconcile conflicts against current production behavior rather than blindly choosing the preview side.
   - Run focused backend tests, frontend tests, lint, build, and `git diff --check` on the exact integrated tree. Commit and push that exact state before deployment.
   - Before deployment, integrity-check and snapshot mutable production data plus currently served artifacts. When the service account cannot write into the operator's backup directory, create the database-native snapshot in a service-writable temporary location, then transfer ownership and move it into the protected backup directory; verify the copied database independently before proceeding.
   - Deploy the committed API/frontend artifacts atomically where practical, preserving runtime uploads/data. Do not assume a running process proves its executable path still exists: preflight the configured `ExecStart` parent directory and recreate/install deliberately when needed. Then verify service health, the running process start time, binary identity, and the public asset hash.
   - Run a public authenticated E2E against production that proves the approved behavior and authorization scope. Avoid mutating production merely for verification when an existing safe record demonstrates the behavior. If credentials are unavailable, perform and clearly label public render plus unauthenticated-contract checks rather than implying authenticated coverage.
9. Before handoff, report branch, HEAD, clean/dirty state, untracked artifacts, validation evidence, preview or production URL, and deployment isolation.
10. For repository-wide canonical-branch realignment, do not equate the word `main` with the actual remote default or production branch. Confirm `origin/HEAD`, source provenance of the live artifact, and the intended branch rename/cutover before creating or pushing a new primary branch. If the repository has no remote, complete and verify the local canonicalization and live deployment, but label it **local canonical main**; do not imply a remote default-branch cutover or invent a remote URL. Preserve dirty topic work separately, integrate only approved coherent ranges, and do not deploy a newly assembled tree while broad verification is red without explicit risk acceptance.

See `references/production-promotion.md` for a concise promotion and conflict-reconciliation checklist. See `references/canonical-branch-realignment.md` for divergent repositories with many worktrees, ambiguous default branches, and live-deployment provenance. See `references/external-symlink-canonical-deployment.md` when the canonical tree imports shared source through a symlink; it covers dual provenance, Vite resolution, red-suite gates, artifact hashes, and smoke-script validation.

## Pitfalls

- Applying stale compacted-session constraints to every later request without reconfirming scope.
- Saying only “deployed” while omitting that all source work remains uncommitted.
- Allowing dozens of validated files to remain vulnerable to another agent’s cleanup/reset.
- Committing preview databases, uploaded test media, binaries, or secrets.
- Treating a checkpoint commit as production approval.

## Verification

Run `git status --short`, inspect staged paths explicitly, verify ignored/generated artifacts are excluded, then record `git rev-parse --short HEAD` and the remote preview branch after pushing.