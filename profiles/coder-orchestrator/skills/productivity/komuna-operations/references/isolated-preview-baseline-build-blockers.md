# Isolated preview baseline build blockers

Use when a Komuna feature passes focused tests but a clean preview worktree cannot complete the app build because of unrelated upstream code.

1. Compare the exact failure with a clean upstream worktree before attributing it to the feature.
2. Check whether tracked source imports a file that exists only as untracked content in the primary checkout; clean worktrees intentionally omit it.
3. Prefer fixing the baseline in its owning workstream.
4. If review must proceed, inspect and temporarily copy only a complete, known-good, non-secret file into the isolated worktree. Never invent a stub or weaken type/build checks.
5. Keep temporary build input untracked and out of the feature diff/commit; disclose the workaround and remove it before integration verification.
6. For a Vite preview at `/previews/<slug>/`, build with `VITE_BASE=/previews/<slug>/` so assets resolve under the isolated route.
7. Report focused feature checks separately from baseline lint/type errors; do not claim the full suite is green.
