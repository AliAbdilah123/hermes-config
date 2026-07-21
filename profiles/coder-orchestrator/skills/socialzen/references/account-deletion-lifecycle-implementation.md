# Account deletion lifecycle implementation

Use this when implementing or auditing SocialZen account deletion/restoration.

## Release checklist

1. Treat password and Google accounts equivalently for recent re-authentication.
   - Password users confirm their current password.
   - Google-only users submit a fresh GIS ID token.
   - Verify the token server-side and require its stable Google `sub` to belong to the same canonical SocialZen user. Never treat matching email alone as sufficient and never let re-auth create/link/switch users.
2. Make the deletion request one short transaction:
   - compare exact `DELETE` confirmation;
   - transition `ACTIVE` → `PENDING_DELETION` with exact UTC deadline;
   - create/reuse one durable pending operation;
   - revoke all sessions;
   - turn overdue scheduled/publishing posts into drafts and future ones into review-required;
   - disable provider credentials while retaining history;
   - stop renewal and clear pending payment intent without inventing refund behavior;
   - append a content-free lifecycle audit event.
3. Check `RowsAffected` on guarded state updates. An idempotent response is valid only when the existing durable operation proves the transition already committed.
4. Emit notifications/email only after commit. In-app delivery may be inaccessible after session revocation, so lifecycle email is not optional when configured.
5. Restoration is a dedicated unauthenticated-but-re-authenticated endpoint. It may reactivate the canonical account and issue a fresh session, but must not reconnect providers, resume billing/sync, or republish queued work.
6. Permanent deletion must be resumable and state-guarded before every irreversible stage. Read candidates into memory and close rows before nested work because production SQLite uses one connection.
7. Keep `db.go` test migration and `internal/models/models.go` production migration synchronized.
8. Do not invent workspace/export/invoice entities. Report zero or explicitly unsupported until a real model exists; enforce ownership transfer only when ownership machinery exists.

## Verification

- Focused tests: impact counts, exact confirmation, bad credentials, password deletion, Google-only deletion, identity mismatch rejection, idempotent request, secure restore, restored-account worker guard, resumable permanent deletion, and login/session blocking.
- Run relevant backend packages and `go build ./...`.
- Run the focused frontend tests, typecheck, and production build.
- Treat unrelated pre-existing full-suite failures separately, but never deploy with a focused/relevant regression.
- Review the actual diff before deployment; delegated summaries are evidence leads, not verification.

## Common pitfall

A password-only implementation appears complete under ordinary fixtures but permanently locks Google-only users out of both deletion and restoration. Include a Google-only fixture before considering Phase 1 releasable.
