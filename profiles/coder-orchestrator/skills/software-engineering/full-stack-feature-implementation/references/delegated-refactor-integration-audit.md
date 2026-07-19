# Delegated Refactor Integration Audit

Use after delegating a broad codebase cleanup or design-system migration.

## Parent-agent acceptance checklist

1. **Inspect the real diff, not the worker summary.** Run status/stat/checks and open the active entrypoint plus representative extracted files.
2. **Prove new architecture is active.** Search production imports and rendered call sites. Config files, installed packages, and generated `components/ui/*` files do not prove migration.
3. **Reject ornamental design-system installs.** For shadcn migrations, require active use of the matching primitives (for example Radix Dialog replacing the hand-rolled dialog), semantic tokens, and removal of unused primitives/dependencies.
4. **Measure decomposition at the entrypoint.** A claimed split is incomplete if the active entry still owns most views and workflows. Keep compatibility re-exports only where tests or callers require them.
5. **Verify delegated scopes together.** Run frontend native tests/build, backend tests/vet/build, and `git diff --check` from the correct package directories after all workers finish.
6. **Deploy in dependency order.** For embedded Vite + Go apps: build frontend, build Go binary, restart service, poll readiness, then compare internal/public asset hashes.
7. **Audit source-control delivery before promising it.** Check remotes early. If no remote exists, commit locally and report push as blocked; never imply a push happened.

## Common false-positive

A worker may truthfully report “real shadcn foundation added” while the live app imports only one primitive and retains custom dialogs/buttons. Search active imports/usages and inspect the mounted app shell before accepting completion.
