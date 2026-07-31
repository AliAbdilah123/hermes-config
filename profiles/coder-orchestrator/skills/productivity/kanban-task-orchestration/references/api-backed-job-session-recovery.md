# API-backed job session recovery

Use when a board job remains `in_progress` after approval or a service restart.

## Evidence order

1. Query the latest job and run together: state, phase, run status, recorded session ID, and timestamps.
2. Interpret `hermes-api:<id>` as an API session identifier—not a tmux session or local process name.
3. Resolve the workspace's persisted Hermes base URL and credential.
4. Fetch session metadata and its message list. Process listings are only relevant to local process-backed runs.
5. Check restart timing and commits/artifacts produced after approval.

## Classification

- **API session active, no final assistant response:** reattach the app watcher. Retrying risks duplicate implementation.
- **Session ended, final response present:** ingest messages and complete the existing run.
- **Session missing or ended without a response:** atomically block run and job, then retry into a new attempt.
- **Commits landed but watcher/result collection stopped:** map commits to exact jobs, run fresh project verification, then repair state atomically.

## Safe manual repair

Before changing a live SQLite database, use `sqlite3 <db> ".backup '<backup>'"`. In one transaction:

- end the exact latest run with an honest summary;
- transition the parent job consistently;
- append reply/status timeline events if the UI depends on them.

Do not fabricate worker output, infer completion from commit existence alone, or set a dead session back to `running`.

## Permanent prevention

Startup reconciliation should inspect every active API-backed run, query the recorded session ID, finish completed sessions, block genuinely missing sessions, and restart watchers for still-active sessions. Cover implementation-phase runs approved immediately before restart.

Add a regression test that seeds an active implementation-phase API run, simulates restart with an API session that is still active, and asserts reconciliation leaves the run active and starts monitoring rather than blocking or duplicating it.
