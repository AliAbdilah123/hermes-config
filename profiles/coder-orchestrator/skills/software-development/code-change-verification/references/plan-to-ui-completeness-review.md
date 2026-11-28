# Plan-to-UI completeness review

Green backend integration tests do not prove a full-stack feature is deliverable. Before release, compare the approved plan with the diff using a capability matrix.

| Capability | Backend read | Backend mutation | Reachable UI control | Visible result/state | Focused test |
|---|---|---|---|---|---|

A row is incomplete if any required cell is missing.

## High-value searches

- API client methods with no callers.
- Response fields defined in types but never rendered.
- Mutation routes tested only through scripts, with no product UI.
- Components that only list data where the plan requires create/edit/delete/assign/pay/pin.
- Hard-coded amounts, currencies, periods, or dates where configuration was requested.
- HTTP 402/409/domain errors routed into generic error screens instead of actionable states.
- One-line generated JSX that bypasses the application's established loading/error/empty/toast/accessibility patterns.

## Release rule

Build, backend tests, and API E2E may all be green while the product remains incomplete. Do not commit/deploy until every planned user-facing mutation is reachable and verified through the frontend, or explicitly marked postponed and approved by the user. After remediation, rerun focused frontend tests plus the complete canonical suite.