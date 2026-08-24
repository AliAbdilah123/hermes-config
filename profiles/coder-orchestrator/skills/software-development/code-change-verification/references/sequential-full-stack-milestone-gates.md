# Sequential full-stack milestone gates

Use for cumulative Go/SQLite/React MVP delivery where each milestone depends on the previous one.

## Per-milestone gate

1. Pin the autonomous coding prompt to one milestone; explicitly preserve prior verified commits and forbid later scope, commits, pushes, and deployment.
2. Treat agent exit `0` as a handoff only. Inspect status/diff, schema and authorization boundaries, then rerun focused race tests, full tests, vet, frontend tests/build, and exact binary build.
3. Use a fresh temporary SQLite file and ephemeral free port. Assert the service-specific health payload so another listener cannot create false evidence.
4. Exercise stateful behavior with separate browser contexts per role. Pair browser assertions with API/DB terminal invariants and `PRAGMA integrity_check`.
5. If a browser locator fails after side effects succeeded, inspect actual labels/IDs and runner APIs before touching product code. Verify committed side effects through API/DB, then rerun the missing browser assertion with stable scoped selectors.
6. Commit only after the gate passes; advance exactly one todo and launch the next milestone.

## High-value state-machine checks

- OTP/session: hashed secrets only, expiry/attempt/single-use, CSRF, revoke/recovery, suspended denial.
- Posts: ownership, filters/pagination, active/expired visibility, transactional tags, reopen persistence.
- Matching: complementary intent, deterministic score/reasons/ties, blocked/own/inactive exclusions.
- Responses/messages: idempotent decisions; accept atomically creates one conversation and two members; third-party denial; bidirectional persisted messages.
- Notifications/workers: transactional notifications, per-user reads, persisted outcome hydration after restart, fixed-time worker rerun with ledger dedupe and retry tests.
- Moderation: bidirectional block effects, admin role from DB, state+audit transaction, immutable audit rows, suspension revokes sessions, reactivation permits new OTP.
- Funnel/hardening: server-derived allowlisted events only, empty/allowlisted metadata, bounded PII-free aggregate, content/body/origin limits, security headers, request IDs, readiness, graceful shutdown, production config fail-fast.

## Status discipline

Use `WORKING` only while a process or verification is actively executing. Agent completion is not milestone completion. If interrupted, report the exact committed boundary and uncommitted milestone state; never imply a temporary server or worker is still active without checking.
