# Live job-session comment composer

Use when a job detail modal must let a user reply to an already-running CLI/agent process.

## Minimal vertical slice

1. Reuse the job's existing authenticated, owner-scoped detail route.
2. Add `POST /jobs/:id/comment` accepting one bounded, trimmed string.
3. Permit comments only while the job has an interactive session (`in_progress` or `blocked`); do not mutate job state.
4. Resolve the newest `running` job run and its persisted tmux/session identifier. Verify the process session still exists before sending.
5. Send the comment verbatim with literal-input mode, then send Enter separately. Never interpolate it into a shell command.
6. Persist a `comment` timeline event against that run and notify the existing SSE/change signal.
7. In the modal, show a textarea for active states, disable blank/in-flight submissions, keep the modal open, clear only after success, refresh detail, and show failures inline.

## TDD checks

- RED first: endpoint is absent and active-state UI predicate is absent.
- Backend: owner isolation, active/inactive state, blank and oversized body, absent process session, successful literal send, event persistence.
- Frontend: composer visibility for active states only, disabled blank/in-flight send, success clear, inline error.
- Run focused tests, then the complete backend suite, frontend suite, production build, service restart, and deployed-bundle marker checks.

## Pitfalls

- Do not reuse a blocked-only `input` action if it changes the job back to todo; comments must be state-neutral and also work during normal execution.
- A running DB row does not prove the tmux/process session exists. Check both.
- Timeline sequence allocation can race the output monitor. Use a transaction/retry or another collision-safe allocator; do not silently ignore a unique-key insertion failure.
- Record the comment only after both process sends succeed, so Timeline does not claim delivery that did not happen.
- Keep approval/retry/cancel controls separate from free-form comments; they have different state transitions.
