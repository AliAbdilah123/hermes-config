# Replying to a completed job reopens execution

Use when a completed job must accept a follow-up reply and run again.

## Minimal model

A completed process session no longer exists, so do **not** pretend this is a live-session comment. Treat the reply as a queued follow-up:

1. Show the existing reply composer for `done` jobs as well as active jobs.
2. Validate and record the reply against the most recent run's timeline.
3. Persist the reply in a small job-level pending field.
4. Atomically move `done -> todo`, clear terminal completion metadata, and signal the existing scheduler.
5. Let the scheduler perform the normal `todo -> in_progress` transition and create a fresh run.
6. Append the pending reply to the new run prompt as an explicit follow-up instruction, then clear it only when the scheduler successfully claims the job.

This preserves the truthful lifecycle: immediately after submission the job may briefly be `todo`; it becomes `in_progress` when execution actually starts.

## TDD checks

- RED: completed jobs reject replies and the composer is hidden.
- Backend: reply to `done` returns success, records a timeline comment, queues the job, preserves the pending reply until claimed, and rejects a completed job with no prior run.
- Frontend: composer is visible for `done`, while remaining hidden for `todo` unless separately requested.
- Scheduler: claimed prompt contains the follow-up reply and the pending field is cleared.
- Run the focused endpoint/UI tests first, then full backend/frontend suites and production build.

## Pitfalls

- Do not send to the old tmux/session ID: completion normally means that process is gone.
- Do not label the job `in_progress` directly in the HTTP handler; only the scheduler should claim execution and create the run.
- Do not clear the pending reply before a successful scheduler claim, or a failed claim loses user input.
- Keep active-session replies state-neutral; only replies to `done` trigger a new execution lifecycle.
- If the backend embeds frontend assets, build frontend first, copy/embed assets, then compile the backend binary. A parallel or reversed build can deploy stale UI even when both builds pass.
