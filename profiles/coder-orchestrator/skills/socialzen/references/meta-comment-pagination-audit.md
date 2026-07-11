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

## Verification

Run from `apps/backend-go`:

```bash
gofmt -w internal/comments/*.go
go test ./internal/comments
go build -o /tmp/socialzen-api .
```

A full `go test ./...` may expose unrelated app tests; do not hide those failures, but the comments regression gate is `./internal/comments`.
