# Read-only attendance analytics implementation

Use this pattern for approved attendance dashboards that serve both broad administrators and narrowly scoped managers.

## Contract and authorization

- Expose separate broad and scoped routes where required, but share the page implementation through an explicit scope mode.
- Enforce program/product scope in the API. Navigation visibility is not authorization.
- Keep the member table read-only; opening details must not imply inline editing.
- Return aggregate metrics, per-member attended and eligible counts, percentage, and session-level records sufficient for the details modal.
- Define the denominator explicitly. Prefer attended divided by eligible held/completed sessions; future sessions must not silently lower attendance. Handle zero eligible sessions without invalid percentages.

## UI behavior

- Sort percentages deterministically with a stable member tie-breaker.
- Make row-triggered details keyboard accessible.
- Identify the selected member in the modal and list exactly which sessions they joined. If missed/upcoming sessions are included, label their states distinctly.
- Support Escape, a labelled close control, one active dialog, and focus restoration.
- Use a scroll-safe or responsive table on narrow screens.

## Verification and delivery

- Backend tests: broad-role authorization, scoped-manager isolation, denominator semantics, and session-detail accuracy.
- Frontend tests: aggregate analytics, deterministic read-only rows, modal contents, and keyboard/dialog behavior.
- Run the canonical frontend build after focused tests.
- In a dirty shared checkout, inspect the baseline, stage only feature-owned paths, run `git diff --cached --check`, and inspect the staged stat before commit.
- Push the focused commit when the workflow requires it, but keep deployment as a separate authorization boundary.