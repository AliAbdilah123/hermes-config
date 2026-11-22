# Durable control-plane vertical slices

Use when evolving an existing dashboard into an operational control plane for jobs, agents, builds, deployments, or other long-running work.

## Minimum slice

Model the durable operation before adding more dashboard widgets:

1. Persist the run/job, ordered steps, optimistic version, and append-only events.
2. Keep draft steps editable only before approval; approval freezes the accepted plan snapshot.
3. Encode lifecycle transitions explicitly and transactionally. Reject stale versions and invalid transitions.
4. Enforce concurrency at the storage boundary. For “parallel workspaces, sequential within one workspace,” use a database uniqueness constraint/index over active workspace states, not a process-local lock.
5. Build list/cockpit, detail/timeline, and lifecycle controls against those contracts.
6. Do not imply autonomous execution unless an actual worker updates durable state and evidence. A monitoring increment may record state without running shell commands.

## Efficient implementation sequence

- Inspect current schema, task identity, project/workspace identity, routes, and UI conventions first.
- Write the approved ordered plan before changing a complex product.
- Branch in place when the user explicitly requested a new branch; preserve unrelated dirty/untracked files and stage exact paths only.
- Follow RED → GREEN for store invariants first, then HTTP contracts, then UI.
- Re-read files after delegated implementation before editing or reviewing; delegated summaries are not source-of-truth.
- Independently review the complete diff, including new untracked assets that do not appear in ordinary `git diff --stat` until staged.

## Verification

Run fresh uncached tests, formatting, vet/lint, build, and frontend syntax checks. Then start an isolated local runtime with a temporary database and unused port; probe both the deep-linked cockpit route and its API. Stop the temporary process afterward.

Before delivery, verify:

- same-workspace active-run collision is rejected;
- different workspaces can become active concurrently;
- stale updates fail;
- every status transition appends an event;
- post-approval step edits fail;
- empty/malformed plans fail at the trust boundary;
- deep links serve embedded assets successfully;
- UI labels distinguish recorded state from actual automated execution.

Commit and push only after independent review passes. Deployment is separate from pushing a feature branch unless the user explicitly approved a preview or production release.
