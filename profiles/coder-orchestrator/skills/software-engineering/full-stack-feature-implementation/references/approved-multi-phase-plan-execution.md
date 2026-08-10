# Approved multi-phase plan execution

Use this when a user explicitly says to start or implement an existing phased plan.

1. Treat that instruction as satisfying the plan's implementation gate; do not request redundant approval.
2. Convert all phases into one tracked task list.
3. For each phase: launch implementation, inspect the resulting diff, rerun focused and full-suite checks independently, then mark it complete.
4. A background-agent completion is only an internal checkpoint. Continue automatically to the next phase unless blocked or a distinct production/deployment gate needs approval.
5. Preserve unrelated dirty/untracked files and keep commit, push, migration, and deployment as separate authorization boundaries.
6. Status terms are literal: **WORKING** while execution runs, **VERIFYING** during independent checks, **STOPPED** when neither is active. Do not call the whole plan ready after an early phase.
7. A diagnosis phase may correctly add tests only when existing production code already satisfies the contract. Accept this only after fresh focused and full-suite runs; never add production code merely to make the phase look substantial.
8. When phases accumulate in one dirty worktree, every later implementation prompt must explicitly preserve prior-phase changes and unrelated untracked files. Review cumulative status/diff, but attribute each phase using changed paths and focused tests rather than assuming every dirty file belongs to the latest phase.
9. Re-run the repository's real gates after every phase (for example focused backend tests, full backend suite, frontend tests, typecheck/build, formatting, and `git diff --check`). Agent-reported results are not verification evidence.
10. For schema-heavy plans, test upgrade paths from the exact prior migration level in an isolated copy of representative real data. Inspect configuration parsing first and use the exact environment keys the service reads; then verify migration version, integrity, foreign keys, and preserved/normalized record counts. A migrated database file proves migration execution, not listener readiness—require a separate health probe before claiming the rehearsal service started.
11. Before the first commit, run one final-state verifier over representative cross-phase behaviors, the full backend/frontend gates, formatting/static checks, and an independent security/logic review. Earlier per-phase output is stale if later phases touched shared code.
12. Keep moving through approved implementation phases after successful verification. Send concise status updates using WORKING/VERIFYING, but do not turn each background-agent completion into a new approval checkpoint.
13. If authenticated public E2E is part of done, keep the final delivery phase active through target discovery, backup, migration, service/static deployment, readiness polling, exact-route browser checks, persistence/reload, and console/network review. Commit/push or a public health response alone is not READY.
