# Feature Status Inventory Docs

Use this reference when the user asks for a repository-level feature list with statuses such as `todo`, `in progress`, `not tested`, `does not work`, and `done`.

## Durable workflow

1. Identify the project root explicitly. If the user says "boilerplate project" or similar, prefer known project directories, but verify by inspecting project names and root files.
2. Read high-signal docs first: root README, backend/API README, deployment docs, PRD/API contract, existing docs, and package scripts.
3. Inspect implementation surfaces without reading dependencies/build output:
   - frontend routes/components/tests
   - backend route registration/handlers/tests/migrations
   - scripts and deployment files
4. Run existing automated verification before assigning statuses when feasible:
   - frontend test command from `package.json`
   - backend test command for the stack (for Go: `go test ./...`)
5. Build a concise Markdown table with columns: `Area`, `Feature`, `Status`, `Notes`.
6. Use status meanings consistently:
   - `done`: implemented and covered by automated tests or verified by a smoke check/documented deployment path.
   - `not tested`: implemented/scaffolded, but not covered by automated tests or not verified against a real third-party service.
   - `in progress`: partial/static/scaffolded/disabled UI or intentionally incomplete real-world integration.
   - `does not work`: confirmed broken behavior from tests, runtime check, or code inspection with clear evidence.
   - `todo`: no implementation found.
7. Include a verification section at the top with the actual commands/results used.
8. Add a "Known does not work items" section. If none are confirmed, say that explicitly rather than inventing broken items.

## Pitfalls

- Do not mark live payment/email/provider integrations `done` solely because request construction is tested. Mark live credentials/real provider behavior as `not tested` unless an actual provider call was run.
- Distinguish backend-only features from frontend availability. If an endpoint exists but no UI exists, list both separately: backend `done`, frontend `todo` or `in progress`.
- Do not include `node_modules`, `dist`, generated bundles, local databases, or build caches in feature discovery except to confirm their existence when directly relevant.
- If the user asked only for a Markdown doc, do not convert it into a styled HTML artifact unless they also request a review/public document artifact.
