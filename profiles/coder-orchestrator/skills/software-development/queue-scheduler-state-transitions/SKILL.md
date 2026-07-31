---
name: queue-scheduler-state-transitions
description: Implement and verify queue schedulers where lifecycle states determine whether the next item may claim a lane, worker, or concurrency slot.
---

# Queue Scheduler State Transitions

Use for job boards, approval workflows, CI queues, worker pools, and other schedulers where an item can remain unfinished without continuing to consume execution capacity.

## Core model

Classify every lifecycle state by **scheduling effect**, separately from its user-facing meaning:

- **Consumes capacity:** actively running, or intentionally holding a lane/worker slot.
- **Releases capacity:** awaiting review/approval or otherwise idle, even if not complete.
- **Policy-dependent:** blocked/error states may reserve capacity to force intervention or release it to maximize throughput. Preserve the product’s explicit policy.

Do not assume “not done” means “blocks the queue.” State transitions and scheduling capacity are separate concerns.

## Implementation workflow

1. Locate the actual eligibility predicate and atomic claim operation.
2. State the intended blocking and non-blocking sets before editing.
3. Add a focused failing regression first.
4. Make the smallest predicate change that reflects the intended sets.
5. Keep the claim atomic; selection eligibility alone does not prevent duplicate starts.
6. Verify the changed non-blocking state and every neighboring blocking state.

For SQL schedulers, a narrow change to a `NOT EXISTS` state set is preferable to adding a second scheduler path when the existing claim operation already provides concurrency safety.

## Focused regression contract

Create a predecessor in the state being reclassified and a following queued item in the same lane. Run one scheduling pass, then assert that the following item was genuinely claimed:

- state changed to running/in-progress;
- attempt count incremented;
- one running execution record exists.

Do not settle for asserting that a query returned the item.

Add or preserve separate cases showing active-running and policy-blocking states still prevent the next item from starting.

If execution launches asynchronously, use a fake downstream service held open by a channel. Inspect claimed/running state while it is blocked, then release it in cleanup so shutdown cannot hang or leak goroutines.

## User-facing queue versus execution status

When the product must differentiate waiting from active provider work, first check whether existing lifecycle states already encode that boundary. Prefer a presentation-only mapping when they do:

- queued/waiting state (for example `todo`) → explicit static label such as “Job queued”;
- claimed/running state (for example `in_progress`) → explicit active label such as “Provider is processing…”;
- review, blocked, and completed states → no live-execution indicator unless the product specifies one.

Do not add a database state, API field, or scheduler transition merely to expose wording already derivable from the canonical lifecycle state. Reserve motion for genuine active work; a queued indicator should be visually static so waiting cannot be mistaken for execution. Keep labels available as text and use `role=status` or live-region behavior only where announcements are useful.

Focused UI regressions should assert both text and semantics: queued renders its static marker without active animation, running renders the processing marker, and neighboring non-live states render neither. If the provider has a private upstream queue that the API does not expose, state that boundary rather than pretending the local queued state represents it.

## Verification

- Copy the exact test name from source or list tests before filtering.
- Anchor exact test filters where supported.
- Treat “no tests to run” as failed verification even if the test command exits zero.
- Run the focused test, then the relevant package/module suite.
- After deployment, use two safe queued fixtures to verify the actual transition when feasible.
- Service-active and HTTP 200 checks prove availability, not scheduler behavior. If authenticated behavioral E2E is unavailable, report that boundary explicitly.

## Pitfalls

- Removing a review state from a blocking set while accidentally weakening blocked/running behavior.
- Testing lifecycle labels instead of claim-side effects.
- Allowing fake executions to finish before assertions, making state checks race-prone.
- Reporting a zero-exit filtered test command that matched no tests.
- Calling deployment E2E-verified based only on process health or an HTTP response.

See `references/review-state-capacity.md` for a concrete state-table and deterministic test recipe.