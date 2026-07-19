# Job Action UI / Backend State Contract Drift

Use this when Retry, Archive, Cancel, or similar job controls are visible but appear to do nothing.

## Diagnosis

1. Trace the click handler to the exact method and route.
2. Read the backend state guards for that route.
3. Compare UI visibility/enabled-state rules with backend-accepted states.
4. Confirm whether rejected API errors are surfaced in the UI; an uncaught `409` often looks like a dead button.
5. Check tests on both sides. Separate tests asserting “button is visible in every state” and “backend rejects non-done state” can both pass while encoding a broken cross-layer contract.

## Fix decision

Choose one product contract, then align both layers:

- If the action is valid only in certain states, hide/disable it elsewhere and explain why.
- If the action is intentionally available in every state, remove the stale backend restriction.

For process-backed jobs, Retry or Archive of an active job must terminate the old worker/session before resetting or deleting state. Otherwise the old process can continue writing events or mutate a retried/deleted job.

## Regression coverage

Prefer an API-level state-transition test that exercises each intended source state and verifies:

- Retry succeeds and resets the job to the queued/todo state.
- Completion timestamps are cleared where appropriate.
- Archive succeeds and removes dependent run/event records transactionally.
- Cross-user access remains rejected.

Also retain a small frontend assertion for action visibility, but do not treat it as sufficient proof of behavior. Run the targeted failing test first, then the backend suite, frontend suite, and production build.
