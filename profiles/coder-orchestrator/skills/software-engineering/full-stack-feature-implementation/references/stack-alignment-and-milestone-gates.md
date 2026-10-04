# Stack alignment and milestone gates

Use this when an approved plan names a provisional stack but the user later says to use the organization's established stack.

## Stack alignment

1. Inspect the organization's canonical boilerplate/repository before changing the feature project.
2. Treat its runtime, package manager, frontend libraries, persistence, routing, deployment, and test conventions as authoritative.
3. Translate the approved product capabilities onto that stack; do not preserve provisional infrastructure merely because it appears in the older plan.
4. Remove unnecessary infrastructure rather than adding compatibility layers. Example: for a one-host pilot, SQLite plus an in-process event hub and durable event table can replace PostgreSQL/Redis/containers until multi-instance operation is required.
5. Do not modify the canonical boilerplate while using it as a reference.
6. Record any deliberate scale ceiling in one concise `ponytail:` comment with the evidence-triggered upgrade path.

## Ordered milestone execution

- Dispatch only the current milestone. Explicitly forbid work on the next milestone.
- Include the exact acceptance gate in the implementation brief.
- Require focused gate tests, full backend tests/static checks/build, frontend tests/typecheck/build, and a live protocol or HTTP check where applicable.
- A worker's summary is not evidence. Inspect the resulting tests and rerun the focused acceptance gate from the final workspace.
- If the worker reports general checks but omits an acceptance behavior, keep the milestone unverified and test that behavior before advancing.
- Distinguish integration tests using an in-memory handler from native live-server E2E. Use both when the gate depends on startup, routing, cookies, streaming, or reconnect behavior.
- Do not call a milestone READY until the exact gate passes. Use WORKING/VERIFIED language accurately.

## Native/no-container delivery

When containers are explicitly excluded:

- Provide one-command native development and verification paths.
- Use the stack's native database migration/bootstrap path.
- Supply systemd/nginx artifacts only when they match the established deployment convention.
- Do not retain Docker-only services as blockers; replace them with approved native equivalents or clearly defer scale-only components.
