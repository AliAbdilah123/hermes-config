# Feature delivery in a dirty shared worktree

Use this pattern when an existing full-stack repository already contains unrelated modified and untracked files.

1. Record `git status --short --branch` before work and identify the tracked branch.
2. Explicitly prohibit modifying, reverting, staging, or committing unrelated paths.
3. Prefer adding clean route/handler files over touching an already-dirty central file when the framework permits it; do not distort architecture merely to avoid a necessary edit.
4. Follow TDD at each changed boundary: focused API and UI tests should fail for the missing behavior before implementation.
5. Stage feature files by exact path and review `git diff --cached`; never use broad staging in a dirty worktree.
6. Commit and push only after fresh focused tests and the canonical build. Confirm local `HEAD` equals the tracked remote SHA after push.
7. Preserve unrelated dirt exactly. Report broader-suite failures separately, and call them pre-existing only when comparison against unchanged `HEAD` or equivalent evidence proves it.

## Verification path discipline

Monorepos may have nested module/package roots. Run checks from the owning module root (for example, the directory containing `go.mod`) rather than assuming a higher-level directory is valid.

Package-manager wrappers can trigger installation or policy hooks before running a local tool. Prefer the canonical command; if the wrapper would mutate dependencies or fails in install policy, invoke the already-installed local binary directly and report the exact fallback command. Do not turn a transient wrapper failure into a permanent claim that the package manager is unusable.

## Completion boundary

A successful commit and push is not deployment. Verify the public route only when deployment was requested or authorized. Otherwise include the canonical public project link while clearly stating that the new commit is not yet live.