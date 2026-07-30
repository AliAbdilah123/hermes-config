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
8. Before handoff, report branch, HEAD, clean/dirty state, untracked artifacts, validation evidence, preview URL, and production isolation.

## Pitfalls

- Applying stale compacted-session constraints to every later request without reconfirming scope.
- Saying only “deployed” while omitting that all source work remains uncommitted.
- Allowing dozens of validated files to remain vulnerable to another agent’s cleanup/reset.
- Committing preview databases, uploaded test media, binaries, or secrets.
- Treating a checkpoint commit as production approval.

## Verification

Run `git status --short`, inspect staged paths explicitly, verify ignored/generated artifacts are excluded, then record `git rev-parse --short HEAD` and the remote preview branch after pushing.