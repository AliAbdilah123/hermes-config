# Canonical deployment with external symlinked source

Use when the canonical repository tracks a symlink to source outside the repository, such as a shared plugin directory.

## Provenance and reproducibility gate

1. Record the symlink and resolved target. Determine whether target files are tracked elsewhere and identify that repository/ref when possible.
2. Do not call the application repository self-contained or reproducible merely because its `main` branch is canonical. The artifact also depends on the external target unless it is pinned.
3. Build from a clean application worktree while holding the external target fixed. Record both provenances.
4. Vite modules imported through an external symlink may resolve dependencies and relative imports from the real path. If the intended contract is repository-relative imports plus the application's `node_modules`, set `resolve.preserveSymlinks: true`, then rerun build and tests. Treat this as project configuration, not a shell workaround.
5. A successful build after correcting symlink resolution does not waive failing tests. Reproduce and classify broad failures at the untouched canonical baseline. Deploy with red broad checks only after explicit acceptance of named failures and risk.

## Deployment checks

- Discover the exact backend main package with language tooling; do not infer its directory from service naming.
- Compare installed binary and deployed static-index hashes with built artifacts.
- Poll readiness after restart; an initial connection refusal may be a normal startup race.
- Verify public HTML, referenced JS/CSS and MIME types, API health, and a safe authenticated read flow.
- Inspect repository smoke scripts before relying on them: configured port, credentials, route contract, and authorization header. A partially passing script with stale defaults is not a green gate.

## Reporting

State application SHA, external-source provenance, remote default, broad-test status, backup path, readiness, public artifact checks, and preserved untracked work.