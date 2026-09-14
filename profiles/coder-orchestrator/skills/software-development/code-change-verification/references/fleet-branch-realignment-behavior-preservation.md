# Fleet branch realignment: preserve behavior, not just ancestry

Use when consolidating many feature branches/worktrees into a canonical branch and rebuilding live applications.

## Core invariant

A commit being an ancestor of `main` does **not** prove its behavior survived later merges. Conflict resolution can retain the commit in history while silently replacing its code. Treat ancestry as provenance evidence only; verify behavior independently.

## Per-repository sequence

1. Inventory nginx route/domain, document root, upstream service, repository, remote, branches, worktrees, stashes, and dirty/runtime files.
2. Preserve unknown dirty state before integration. Never delete a branch/worktree merely because its commits are reachable.
3. For each feature branch, identify its user-visible or data-integrity behavior and the files/tests that embody it.
4. Merge with normal merge commits when requested. Resolve conflicts semantically; do not default wholesale to `ours` or `theirs` in high-churn files.
5. After every conflict resolution, build a **behavior preservation ledger**:
   - feature/commit;
   - expected behavior marker or focused test;
   - final canonical source evidence;
   - focused test result;
   - deployed evidence when applicable.
6. Before pruning, require both:
   - history integration (`merge-base --is-ancestor`, cherry comparison); and
   - behavior integration (focused regression or exact source/render assertion).
7. Build and deploy only from the final canonical checkout. Compare built and served artifact hashes, resolve lazy route chunks when needed, and verify the exact public route/state.
8. Push and compare local/remote canonical SHAs. Prune only clean, unused refs/worktrees whose behavior ledger is complete.

## Conflict-heavy UI files

For large React pages that accumulate several features:

- Diff the pre-merge feature tip against the resolved canonical file, not only the merge commit graph.
- Search for distinctive labels, partition rules, callbacks, route IDs, and accessibility attributes introduced by each feature.
- Add a focused regression before deployment for any behavior that lacked one.
- For drag-and-drop layouts, assert both presentation and unchanged data semantics: existing droppable IDs, original unpartitioned draggable indexes, and no accidental new mutation boundary.

## Fleet completion gate

Independently recheck worker summaries. A subagent exit or “active” claim is not evidence. Confirm actual unit names/listeners, public routes, asset MIME types, final SHAs, and exact behavior markers. If a worker summary omits SHA, push, deployment, or runtime details, recover them before reporting completion.

## Failure pattern to prevent

A feature commit may appear in `git branch --contains` and still be absent from the live UI because a later merge conflict restored an older rendering block. A build and HTTP 200 will not catch this. The focused behavior test and deployed lazy-chunk/render check are the required gates.
