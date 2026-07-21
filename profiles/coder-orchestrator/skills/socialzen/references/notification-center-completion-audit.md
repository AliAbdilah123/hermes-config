# Notification Center Completion Audit

Use this after implementing an approved SocialZen Notification Center plan and before claiming the plan is complete.

## Audit method

1. Convert every plan task and acceptance check into an `Implemented / Partial / Missing` matrix. Evidence must be actual `file:line`, a passing test, or a production response—not a commit summary.
2. Review backend, frontend, and end-to-end wiring independently. For a large change, use fresh reviewers for each area; the implementer’s report is not verification.
3. Distinguish framework code from live producers. A helper supporting an event does not mean that event’s committed mutation path calls it.
4. Re-run focused notification tests, backend build, frontend typecheck/build, then full suites. Classify unrelated baseline failures separately; never describe a build as a full-suite pass.
5. Production health and JS content type are deployment checks only. Authenticate with a test session and smoke list, unread count, detail, read/archive/unarchive/delete, mark-all-read, and preferences before claiming end-to-end completion.

## High-risk completeness checks

- **Publishing:** producer runs only after target and parent status commit; 60-second grouping separates success/failure; snapshots include every target result; dedupe is per target/result transition; restart reconciliation cannot silently omit older final rows because of a small fixed limit; quota failures are included; unavailable posts disable actions while history remains.
- **Analytics:** evaluation occurs after exact `post_target_metrics` persistence and uses `post_target_id`; all promised metrics are actually populated by production metric extraction (not merely listed in threshold constants); simultaneous crossings batch; stable threshold dedupe and six-hour cooldown work; suppressed milestones are not backfilled; exact post/target query selection is honored in the UI.
- **Accounts:** connect/disconnect hooks exist for Instagram, Facebook, and Threads; token-state transitions and expiry warnings are actually scheduled/delivered and deduped by account + expiry + warning window.
- **Security/subscriptions:** email verification and password mutations notify only after commit; every promised subscription/billing transition is wired at its real completion/webhook boundary with provider event dedupe. A `plan_changed` service case without a caller is Partial, not Implemented.
- **Exports:** if no export subsystem/callback exists, mark the producer conditional/not applicable; do not imply it was implemented.
- **Retention:** protected categories are indefinite; Analytics and Publishing boundaries match the plan; maintenance runs at startup/daily and is bounded.
- **API/security:** all routes authenticate and scope by user; cursor is `(created_at,id)`; enum/limit/cursor/JSON validation exists; deep links are allowlisted server-side; external links require HTTPS and `noopener noreferrer`.
- **Frontend:** bell appears through shared Topbar on every authenticated route, including exceptional mobile Settings headers; polling runs only authenticated/visible and refreshes on focus; badge has accessible unread text; dropdown handles keyboard/Escape/outside click; list supports search/category/unread/archive/load-more; detail renders all grouped items and category actions; read/archive/delete immediately reconcile local badge/list state.

## Reporting

Do not answer “everything is implemented” unless every non-conditional row is Implemented and authenticated production mutations were exercised. Report gaps first, with severity and evidence, then summarize verified coverage and checks run. If the audit finds gaps after deployment, say the earlier completion claim was too broad and obtain/confirm implementation authorization before changing production again.
