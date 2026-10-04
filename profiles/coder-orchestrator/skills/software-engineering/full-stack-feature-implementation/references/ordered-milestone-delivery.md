# Ordered milestone delivery for large feature sets

Use when a complex feature is approved as an ordered plan and every milestone must verify before the next starts.

## Execution loop

1. Create one feature branch before implementation.
2. Assign only the current milestone to a worker. Explicitly prohibit later scope, commits, pushes, deployment, and plan edits.
3. Require RED evidence, minimal implementation, focused GREEN, full tests, lint, typecheck, and production build.
4. Treat worker output as a claim: inspect changed paths and critical logic, then rerun focused and full gates from the shared final workspace.
5. Advance only after independent verification. If a worker or runner fails before changing code, classify it as orchestration/setup failure—not a product milestone failure—and use another available implementation path without weakening the milestone gate.
6. After the final milestone, run an independent code review before commit. Fix blocking findings and rerun the entire gate.
7. Build cleanly, deploy the exact build artifact, compare deployed/source artifacts where possible, and verify local plus public endpoints.
8. Perform authenticated/public browser E2E when applicable, including console/page errors and desktop/mobile overflow. Prefer DOM-specific assertions (`main h1`, scoped regions) when accessible-name queries include nested descriptive text or duplicate navigation labels.
9. Keep commit, push, and deploy as separate states. Never report push when no remote exists.

## Status communication

Use `WORKING` while implementing, `VERIFYING` during fresh final checks, and `READY` only after public E2E succeeds. Report the current milestone and compact evidence; do not imply overall completion from a worker’s self-report.

## Partial milestone gates and unavailable infrastructure

A delegated implementation can be code-complete while its milestone remains unverified. After the worker returns:

1. Inspect repository paths and critical implementation rather than accepting its summary.
2. Rerun native tests, static checks, and production builds from the final workspace.
3. Exercise every service endpoint that can run locally. For readiness probes, verify liveness succeeds and missing dependencies produce the documented failure response.
4. Treat a test command reporting zero tests as a verification gap, not evidence that frontend behavior passed.
5. Parse deployment, OpenAPI, and CI configuration statically when runtime infrastructure is unavailable, but do not equate parsing with starting services.
6. Keep the milestone below `READY` until required databases, queues, object stores, migrations, and dependency-backed readiness checks actually run. State the exact remaining gate and ask only for the access or setup permission needed to close it.

Do not encode a temporarily missing binary as a durable project limitation; preserve the distinction between verified code, statically validated configuration, and runtime proof.

## Pitfalls

- Do not let a failed preferred coding-agent credential become a reason to stop product milestones if another approved execution path exists.
- Do not run a test file with the wrong runner; inspect its imports/framework first.
- Do not repeatedly retry an E2E assertion unchanged. Debug URL, role state, DOM, and selector ambiguity separately.
- Do not trust generated `dist/` from a worker. Remove it and make a clean build before deployment.
- Do not mark a milestone ready because its build passes when its acceptance gate explicitly requires live infrastructure or migrations.
