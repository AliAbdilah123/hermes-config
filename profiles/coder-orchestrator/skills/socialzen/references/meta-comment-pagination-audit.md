# Meta comment pagination audit pattern

Use this when SocialZen comments/replies are missing or the reply UI count/thread looks wrong.

## Root cause pattern

Meta comment edges are cursor-paginated. A sync that fetches only the first page, or relies on embedded `replies{...}` data, will undercount comments/replies.

- Instagram media comments: `/{ig-media-id}/comments`
- Instagram comment replies: `/{ig-comment-id}/replies`
- Facebook post/object comments: `/{object-id}/comments`
- Facebook comment replies: `/{comment-id}/comments`
- Continue following `paging.next` until empty for both top-level comments and replies.

## SocialZen implementation checklist

- Start sync from `post_targets.platform_post_id`, not the local post ID.
- Resolve the token from the matching account table:
  - Instagram: `instagram_accounts.access_token_encrypted`
  - Facebook: `facebook_pages.access_token_encrypted`
- Fetch top-level pages with `limit=100` and explicit fields.
- For every top-level provider comment, upsert it first and reuse any existing local row with the same `(user_id, media_id, instagram_comment_id)` so replies attach to the visible parent.
- Fetch replies from the separate provider reply edge and paginate that edge too.
- Preserve local parent-child mapping via `parent_id` after resolving the provider parent to its local row.
- Keep the frontend simple if it already renders `comment.replies`: fix the backend data shape before changing UI state.
- Add targeted regression tests with a fake Graph server that returns:
  1. two top-level pages via `paging.next`, and
  2. two reply pages via `paging.next`.

## Logging

Graph logs should include the provider, redacted endpoint, whether a cursor page exists, item count, response status/body snippet, and errors. Never log raw access tokens; redact `access_token` query params and token strings in bodies.

## Reconnected-account identity drift

A published target can retain an old internal `instagram_accounts.id` after disconnect/reconnect while the replacement ACTIVE row has the same external `ig_user_id`. If sync resolves only `post_targets.account_id`, it can stop with `instagram account not connected` before making any Meta request even though that Instagram account is currently connected.

Resolution rules:

- Prefer the exact active internal account row referenced by the target.
- Otherwise, read the old row’s external `ig_user_id` and use a replacement only when exactly one ACTIVE direct-Instagram row for the same user has that `ig_user_id`.
- Never fall back to merely “any active Instagram account”; that risks using another account’s token.
- Reject ambiguous duplicate active matches rather than guessing.
- Add regression cases for one safe same-external-ID reconnect and two ambiguous active replacements.
- Keep identity repair separate from pagination and permissions: zero outbound requests indicates account resolution failed before Meta; `data:[]` proves Meta was called and returned no comments.

The shared account resolver may also restore exact-media analytics calls. It does not justify adding OAuth permissions.

## Verification

Run from `apps/backend-go`:

```bash
gofmt -w internal/comments/*.go
go test ./internal/comments
go build -o /tmp/socialzen-api .
```

A full `go test ./...` may expose unrelated app tests; do not hide those failures, but the comments regression gate is `./internal/comments`.
