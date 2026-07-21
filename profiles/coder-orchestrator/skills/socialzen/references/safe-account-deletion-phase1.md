# Safe account deletion: Phase 1 implementation

Use this recipe when implementing account deactivation, grace-period restoration, and eventual permanent deletion in SocialZen.

## Minimal state model

- Add `users.account_state` (`ACTIVE`, `PENDING_DELETION`) plus request/due timestamps.
- Keep a durable `account_deletion_operations` row with `PENDING`, `RESTORED`, or `COMPLETED`; enforce at most one pending operation per user with a partial unique index.
- Keep immutable, content-free lifecycle audit rows with actor, action, correlation/operation ID, result, and timestamp.
- Apply schema changes in both migration paths: test/legacy `app.migrate()` and production `models.Migrate()`.

## Request boundary

1. Resolve identity only from the authenticated session; never accept a user ID.
2. Return real impact counts scoped by that user. Report zero for entity types that do not exist rather than inventing workspace/export/invoice models.
3. Require recent credential proof and exact `DELETE` confirmation. Password users can re-authenticate inline; Google-only users require a verified Google re-auth path before this is complete.
4. In one short transaction:
   - move the account to `PENDING_DELETION` and persist the exact 30-day deadline;
   - create/reuse the durable operation;
   - revoke every SocialZen session;
   - turn overdue scheduled/publishing posts into drafts and future ones into `REVIEW_REQUIRED`;
   - disable provider rows and clear credentials where schema permits;
   - prevent subscription renewal and clear pending payment state;
   - write the audit event.
5. Commit before sending deduplicated Notification Center/email messages.

All session lookup paths and both email/Google sign-in must reject non-`ACTIVE` users. Blocking only the UI is insufficient.

## Restoration

- Expose a dedicated unauthenticated endpoint with strong credential verification because deletion revoked all sessions.
- Atomically change only a matching `PENDING` operation to `RESTORED` and the user back to `ACTIVE`.
- Make repeated restoration idempotent.
- Issue a new session only after commit.
- Never reactivate provider credentials, billing, sync, or queued publishing. Future schedules remain review-required; overdue schedules remain drafts.

## Permanent deletion worker

- Select due `PENDING` operations in a bounded batch, close `Rows`, then process each operation separately (single-connection SQLite rule).
- Inside each transaction, re-read `users.account_state` immediately before irreversible work. Exit if restoration won.
- Explicitly delete user-owned dependants before `users` because legacy SocialZen tables have incomplete cascades. Include notifications/outbox/preferences/processed markers, comments, hashtag history, media, metrics, targets, post media, quota, posts, subscriptions, auth tokens, identities, sessions, and provider accounts.
- Keep `account_deletion_operations` and safe lifecycle audit metadata outside the user cascade so completion remains auditable.
- Mark completion only after all deletion steps succeed; reruns must no-op.
- Run once at startup and from the existing daily maintenance ticker.

## UI

- Replace the Settings placeholder with Account & Data impact counts and retention disclosure.
- Final dialog requires password plus exact `DELETE` and displays the concrete proposed deletion date, not only “in 30 days.”
- After success, clear local session state and route to sign-in.
- Pending accounts should see a dedicated restoration entry from sign-in; ordinary sign-in remains blocked.

## TDD and verification

Write RED tests first for:

- real, user-scoped impact counts;
- bad password and non-exact confirmation rejection;
- atomic deactivation (sessions revoked, providers disabled, schedules reviewed/drafted, renewal stopped);
- ordinary email and Google login blocked;
- secure, idempotent restoration with no automatic resumption;
- state-guarded, resumable worker deleting a user with dependent rows;
- exact frontend confirmation helper.

Then run focused deletion tests, relevant backend packages, `go build ./...`, focused Vitest, TypeScript typecheck, and a fresh Vite build. Also attempt the full suite, but report unrelated pre-existing failures separately rather than representing focused success as a globally green suite.

## Pitfalls

- `DELETE FROM users` alone is unsafe: legacy foreign keys/cascades are inconsistent.
- Disabling provider status without clearing credentials does not satisfy immediate credential deactivation.
- Revoking sessions does not block Google sign-in; every login method needs the account-state gate.
- Notification deep links must be added to the structural allowlist before delivery or candidate validation rejects them.
- Do not claim equivalent Google re-auth is complete when only password confirmation exists.
- Do not claim reminder delivery, provider-side OAuth revocation, legal retention, invoices, workspace ownership, or export cleanup unless those entities/integrations were actually implemented and tested.
