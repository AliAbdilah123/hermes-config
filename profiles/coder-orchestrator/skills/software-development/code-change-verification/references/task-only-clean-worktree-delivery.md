# Task-only clean-worktree delivery

Use this when implementation in a shared checkout becomes mixed with unrelated concurrent edits and the task still needs a trustworthy commit, build, and deployment.

## Pattern

1. Record the upstream baseline commit and the exact task-owned files/behaviors.
2. Create a fresh branch worktree from that baseline using `git worktree add -b <task-branch> <path> <baseline>`.
3. Reproduce only the task delta in the clean worktree. If a coding agent is used, explicitly allow the dirty checkout as read-only reference and forbid copying unrelated changes.
4. Add only focused regression tests for the approved behavior. Do not import tests or helpers belonging to concurrent work.
5. Run, in order:
   - focused behavior tests;
   - full package test suite;
   - typecheck/build;
   - `git diff --check`;
   - a directly executed `/tmp/hermes-verify-*` script containing the focused test plus build.
6. Inspect the clean diff and stage explicit paths only.
7. Commit and push the task branch. Verify the task commit is contained by the remote branch.
8. Deploy from the verified clean worktree artifact, not from the dirty shared checkout.
9. Verify the live document root serves the new asset names and inspect the deployed JS/CSS for stable semantic markers from the change.
10. Exercise the exact public interaction. If browser E2E remains unavailable, report the narrower truth: deployed with tests/build and served-marker verification, but public interactive E2E is still pending.

## Important distinctions

- A clean worktree protects task scope; it does not authorize discarding concurrent edits in the main checkout.
- Reproducing a task delta in a clean worktree is preferable to trying to surgically stage interleaved hunks from files modified by multiple workers.
- HTTP 200 and bundle-marker checks prove transport/deployment freshness, not the interactive new-tab, popup-blocking, persistence, or state-transition behavior.
- A failed chained verification command may occur after a successful deployment copy. Inspect each side effect independently before retrying; do not blindly redeploy.
