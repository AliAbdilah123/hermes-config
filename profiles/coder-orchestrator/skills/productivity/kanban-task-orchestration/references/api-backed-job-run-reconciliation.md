# API-backed Job Run Reconciliation

Use when a board job remains `in_progress` after an application restart or appears to have stopped producing events.

## Diagnose by runner type

1. Read the latest job and run together: job state/phase, run status, timestamps, and the exact stored session identifier.
2. Do not infer session death from absence of a local Codex/Hermes child process. For an API-backed run such as `hermes-api:<session-id>`, query the workspace's configured Hermes session and messages endpoints.
3. Inspect service restart history around the last event. A restart may interrupt only the board's watcher while the remote worker keeps running or finishes normally.

## Recovery decision

- **Remote session completed:** inspect its messages and resulting commits/artifacts, independently verify them, then finalize the existing run and job. Do not retry and duplicate implementation.
- **Remote session is authoritatively absent/terminated:** atomically block/end both run and job with an actionable warning, then retry to create a new attempt.
- **Remote API has a transient transport/5xx failure:** leave the current run active and poll again. One failed reconciliation request is not evidence that the session is gone.

## Durable watcher rule

Startup reconciliation must attach a watcher to every current API-backed `running` run. The watcher should continue after transient API failures while the DB run remains the latest active run. It should stop only when:

- the remote session returns a final response;
- the remote session authoritatively ends without a response;
- the run/job is explicitly cancelled, blocked, replaced, or otherwise ceases to be current.

## Regression test

Create an implementation-phase job and current `running` API-backed run. Make the session endpoint return `503` once, then return an active session and a final assistant message. Invoke startup reconciliation and assert that:

- polling occurs again after the first failure;
- the existing run becomes `done`;
- the job becomes `done`;
- no second attempt/run is created.

## Deployment verification

1. Run the targeted regression test and full backend suite.
2. Build the actual service binary used by systemd.
3. Restart the service and confirm it remains active.
4. Query for current `running` runs and ensure each has a watcher-compatible stored session.
5. Verify the public application route, then confirm commit and remote branch match.
