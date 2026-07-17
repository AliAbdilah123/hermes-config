# Tmux-backed Job Runner Session Lifecycle

Use when a web job board reports a job as `running` or `blocked`, but interactive input/replies fail with an error such as `active session not found`.

## Diagnosis

Treat database run state and process state as separate sources of evidence:

1. Query the job and latest run together: job state, run status, recorded tmux session, attempt, and timestamps.
2. Check the actual session as the same OS user as the service:
   - `tmux list-sessions`
   - `tmux has-session -t <recorded-session>`
3. Inspect recent service restarts and the systemd unit. A restart can kill child tmux processes while leaving `job_runs.status='running'` stale.
4. Reproduce the reply path only after confirming the session exists. A valid database row does not prove an interactive process is alive.

## Durable Fix Pattern

### Preserve detached sessions across app restarts

For a service that intentionally launches detached tmux sessions which must outlive the web process, use a systemd drop-in:

```ini
[Service]
KillMode=process
```

Then run `systemctl daemon-reload` and restart the service. Use this only when child-session persistence is intentional; otherwise keep systemd's default cgroup cleanup.

### Reconcile both halves of stale state

At startup, inspect every `job_runs` row whose status is `running`, using its recorded `tmux_session` value rather than reconstructing a name from the job ID. If the session is absent:

- mark the run `blocked` (or failed), set `ended_at`, and record a clear summary;
- mark the parent job `blocked` with the same actionable warning;
- emit an event if the UI timeline depends on events.

Do not reconcile only jobs in `in_progress`. A job may already be `blocked` while its latest run remains incorrectly `running`, causing reply controls to appear but all sends to fail.

## Recovery

A missing tmux session cannot be resumed. Explicitly retry/requeue the affected job to create a new attempt and session. Do not merely change the stale run back to `running`.

## Regression Test

Create a job plus a `running` run whose `tmux_session` does not exist, invoke startup reconciliation, and assert:

- run status is no longer `running`;
- job state is `blocked`;
- both carry the expected missing-session explanation.

## Deployment Verification

1. Start/retry a harmless job and confirm the run is `running` and tmux session exists.
2. Restart only the web service.
3. Confirm the tmux session still exists.
4. Confirm database job/run states remain active.
5. Send harmless literal input with `tmux send-keys -l` and verify success.

Avoid pressing Enter during a preservation smoke test unless executing the input is intended.