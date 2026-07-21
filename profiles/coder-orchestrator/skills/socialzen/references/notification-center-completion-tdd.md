# Notification Center Completion Fixes with Strict TDD

Use this when closing gaps found by the Notification Center completion audit.

## Completion discipline

- Turn each of the ten approved completion fixes into an explicit checklist before editing. Do not substitute newly discovered fixes for the requested ten or stop after a partial subset.
- For every behavior, preserve RED evidence: add the smallest focused test, run it alone, and confirm it fails for the intended missing behavior before production edits.
- Run GREEN immediately after each minimal fix, then run the focused notification suites after related fixes are grouped.
- After the final edit, run fresh verification again. Earlier passing output is stale once any tracked source changes.
- Required final checks: notification-focused Go tests, notification-focused frontend tests, frontend typecheck, `pnpm run build`, and `go build ./...`. Run full suites separately and classify unrelated baseline failures without presenting them as feature failures.
- If any requested completion row remains Partial/Missing, continue implementing rather than presenting a completion summary. If genuinely blocked, name the exact row and blocker.

## High-value regression shapes

- **Restart reconciliation:** seed more rows than the old fixed query limit and assert every committed final publishing target is queued. A fixed `LIMIT 100` can permanently omit older targets; reconciliation must page exhaustively or process all rows.
- **Archived mark-all-read:** request `archived=true`, assert the archived row's `read_at` changes, and pass the archived filter from frontend to API. A response count alone is insufficient evidence.
- **Deep-link allowlist:** reject syntactically internal but unapproved routes and traversal strings (for example `/app/admin` and `/app/posts/../../admin`), while retaining every explicitly supported destination.
- **Token expiry warnings:** seed Instagram, Facebook, and Threads accounts with the same warning-window expiry; assert three deliveries and zero on the repeated run. Materialize and close each provider query before calling delivery under single-connection SQLite.

## Reporting boundary

A focused pass plus successful builds verifies the changed slice, not all ten completion requirements. Do not say “implemented all ten” until the audit matrix has ten Implemented rows backed by tests/file evidence. Never commit or deploy when the user prohibited it.
