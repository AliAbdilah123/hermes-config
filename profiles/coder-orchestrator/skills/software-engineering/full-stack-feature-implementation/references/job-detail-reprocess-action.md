# Job detail reprocess/retry action

Use this pattern when an existing queued-job app needs to rerun a completed job from its detail modal.

## State contract

- Treat **retry/reprocess** as a completed-job transition: `done -> todo`.
- Reject retry from every other state with `409`; do not overload retry as blocked-session resume.
- Keep blocked-session actions separate: approve/input resumes the active session, while cancel returns it to the queue.
- Reset terminal completion metadata such as `finished_at` when returning the job to `todo`.
- Preserve the same job row, task, done definition, timeline, and attempt history. Let the existing scheduler create the next run and increment `attempt_count`.

## UI

- Show `Retry job` only for completed jobs in the existing job-detail modal.
- Reuse the existing action helper: `POST /jobs/:id/retry`, then refresh the board and close or refresh the modal.
- Remove any old retry control from blocked-state controls if its semantics were merely resetting the job to `todo`.

## Focused verification

1. Backend test: a done job retries successfully, becomes `todo`, and has null completion metadata.
2. Backend test: retrying the resulting todo job returns `409`.
3. Frontend build/bundle contains the completed-state `Retry job` control.
4. Restart the service, wait for its readiness/log signal, then verify the public index references the new asset and the asset contains the marker.

## Pitfall

A route being registered does not mean its state semantics are correct. Trace the handler before reusing it: a generic action branch may accept only `blocked` jobs and silently make “retry” equivalent to “resume/reset.” Align route validation, UI visibility, and lifecycle metadata together.
