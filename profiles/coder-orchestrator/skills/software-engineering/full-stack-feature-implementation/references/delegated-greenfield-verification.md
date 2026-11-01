# Delegated greenfield verification

Use this after an autonomous coding agent builds a new full-stack application.

## Independent acceptance pass

Do not treat the agent's final summary as evidence. Independently:

1. Enumerate delivered files and compare them with every explicit requirement.
2. Run formatting, the complete test suite, static analysis, and a production build yourself.
3. Start the built artifact with an isolated temporary project root and database.
4. Probe the root route, a deep link, representative reads, a mutation, and at least one required rejection path.
5. Inspect security- and data-integrity-sensitive code directly: path confinement, database snapshots, secret handling, optimistic concurrency, and forbidden persistence.
6. For an external protocol, inspect the installed/upstream client and server—not only delegate-authored mocks—to confirm methods, authentication, framing, result shape, and completion events.
7. Verify the UI performs the promised behavior rather than merely exposing backend endpoints. An SSE/stream endpoint is incomplete if the client only says “accepted” and never consumes or renders the response.
8. Report exact commands and observed outputs; distinguish mocked contract coverage from a live integration test.

## TDD evidence

For delegated strict-TDD work, retain a concise red/green log, but verify that failures precede production code and fail for the intended missing behavior. A delegate-written log is supporting evidence, not a substitute for observed execution.

## False-completion signals

- “All APIs implemented” while a UI path never invokes one.
- A mock reproduces client assumptions rather than the real provider contract.
- A successful compile is presented as a production build and runtime smoke test.
- A GET endpoint unexpectedly mutates worktrees or databases.
- The final summary omits deferred or unverified acceptance criteria.
