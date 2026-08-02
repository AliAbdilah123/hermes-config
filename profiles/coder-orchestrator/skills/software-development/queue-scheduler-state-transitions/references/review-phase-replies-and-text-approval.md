# Review-phase replies and text approval

Use this when a job runner mistakes a proposal/review response for completed implementation, or approval works only through a button.

## Diagnose

1. Inspect persisted job `state` **and** workflow `phase`; state alone is insufficient.
2. Read the latest run summary and events. Distinguish proposal/review-only output (for example, “no implementation was performed”) from a verified implementation result.
3. Trace completed-job feedback. If requeueing preserves `phase='implementation'`, the next proposal-only run can be finalized as done.
4. Compare button approval with comment/reply handling. Both should call one atomic approval transition.

## Minimal fix pattern

- Feedback to a `done` or `in_review` job enqueues it at the queue tail with `state='todo'`, `phase='review'`, and the pending comment.
- Completion of a review-phase run transitions to `in_review`, not `done`.
- While a job is `in_review`, classify explicit approval replies before generic feedback requeueing.
- Route recognized approval text through the button's existing transaction:
  - persist the reply as a comment;
  - persist an approval event;
  - change `in_review → in_progress` and `review → implementation`;
  - reuse the latest valid run/session;
  - include the reply in the implementation prompt.
- Keep recognition conservative. Normalize case and outer punctuation; accept explicit phrases such as `approve`, `approved`, `go ahead`, `implement it`, `lgtm`, `proceed`, or `ship it`. Do not treat arbitrary praise as approval.

## Regression checks

1. Seed a completed implementation-phase job, submit corrective feedback, and assert `todo/review`.
2. Finish the resumed run with proposal-only output and assert `in_review/review`.
3. Seed an `in_review/review` job, reply “Go ahead with the plan,” and assert `in_progress/implementation`, latest run `running`, exactly one comment event, and exactly one approval event.
4. Preserve the button-approval regression.
5. Run focused lifecycle tests, the package suite, and a build from the actual executable package.

## Repairing existing rows

The code fix does not repair already-misclassified jobs. Correct a reported row separately and transactionally only after verifying its current state and latest reply. Back up the database, preserve event sequence constraints, append an auditable correction event, and verify the exact public detail route shows the corrected status.

For SQLite event tables with `UNIQUE(job_run_id, sequence)`, derive the next sequence inside the same transaction (`COALESCE(MAX(sequence),0)+1`) rather than inserting an event without required ordering metadata.

## Deployment verification boundary

Build from the real command package (a Go module root may contain no root `main`; locate `cmd/<app>`). Service-active and public HTTP 200 prove deployment availability, not reply-driven approval. Exercise the authenticated reply transition before calling the feature READY; otherwise report deployed with authenticated E2E pending.
