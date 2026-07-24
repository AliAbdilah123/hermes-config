# Instagram reconnect resolution for comment and analytics sync

Use this when a published `post_targets.account_id` points to a DISCONNECTED `instagram_accounts` row while reconnecting created a newer ACTIVE row for the same Instagram identity.

## Minimal resolution boundary

Put fallback resolution in the shared Instagram account/token lookup used by both comment sync and metrics/insights refresh.

1. Preserve exact identity: prefer the requested row only when it belongs to the same app user, has `provider='instagram'`, and is ACTIVE.
2. If that row is stale, read its stable external `ig_user_id` and select an ACTIVE row only for the same app user and provider with that exact `ig_user_id`.
3. Require exactly one ACTIVE external-ID match. If multiple rows match, fail closed rather than choosing by recency.
4. Do not rewrite the historical published target merely to make synchronization work.
5. Continue token-presence and expiration validation after resolution.
6. Do not add OAuth scopes for what is an account-row resolution bug.

This preserves exact account identity while allowing a reconnect to supply the current token. Matching only platform, username, or “newest Instagram account” is unsafe.

## Focused TDD shape

- RED fixture: published target references `acct_old`; `acct_old` is DISCONNECTED; `acct_new` is ACTIVE; both belong to the same app user/provider and share `ig_user_id`; assert Graph receives only `acct_new`'s token.
- Safety fixture: two ACTIVE rows share the old row's `ig_user_id`; assert no Graph request occurs.
- Keep existing pagination regression green: top-level `/comments` follows every `paging.next`, and each parent separately fetches and paginates `/{comment-id}/replies`.
- Verify requested comment fields remain `id,text,username,timestamp,like_count` on both edges.
- Test schemas that exercise the production resolver must include `instagram_accounts.status` with an ACTIVE default; otherwise legacy fixtures can fail for schema drift rather than behavior.

## Verification

```bash
cd /home/ubuntu/socialzen/apps/backend-go
go test ./internal/comments -count=1
go test ./internal/comments ./internal/sync -count=1
go build ./...
git diff --check
```

If an external verifier explicitly requires the frontend canonical build despite a backend-only diff, also run `pnpm run build` from `apps/frontend`; report it separately rather than treating it as backend coverage.
