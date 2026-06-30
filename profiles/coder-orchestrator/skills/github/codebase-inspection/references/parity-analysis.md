# Implementation Parity Analysis Workflow

Use when comparing a current implementation against a previous version or alternate stack (for example Go replacement API vs Node.js/Hono backend).

## Minimal workflow

1. Identify both implementations and their intended boundary:
   - current runtime files/routes/services
   - previous implementation files/routes/services/schema
   - frontend API client contract, if applicable
2. Inventory route/API surface mechanically:
   - route registrations
   - HTTP methods and paths
   - special nested endpoints (`/:id/tasks`, `/graph`, `/logs`, bulk actions)
3. Compare behavior classes, not only paths:
   - request/response shape
   - auth/session semantics
   - validation and error behavior
   - persistence model and constraints
   - filtering/search/sort/pagination semantics
   - side effects such as linking subtasks, task ordering, graph aggregation
4. Run at least one real verification command for each side that is runnable:
   - backend tests (`go test ./...`, package test scripts, etc.)
   - frontend build/typecheck when the frontend consumes the contract
5. Produce a concise parity matrix with statuses:
   - Full / Full+ — same or better surface and behavior
   - Partial — route exists but behavior/validation/storage semantics differ
   - Gap — missing or incompatible behavior
6. If the user likes review docs/public links, write a styled HTML report under `docs/` and publish/copy it to the project's public static path; verify the URL returns 200 and contains the report text.

## Pitfalls

- Do not call route-surface parity “full parity” when the storage/auth model changed. A local JSON/SQLite demo backend can match the UI contract while still being non-production parity vs a Node/Postgres/JWT backend.
- Include root cause / impact language for each major gap, not just “missing”. Example: “manual IDs in JSON can drift; deletes may leave orphaned data.”
- Prefer a short report with a matrix and fix order over a long narrative.
