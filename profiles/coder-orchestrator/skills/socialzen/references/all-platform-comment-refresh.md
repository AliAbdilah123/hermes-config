# All-platform comment refresh and visibility

Use when the comments drawer must show every current Instagram and Facebook user comment and reply without requiring close/reopen or manual pagination.

## Root-cause checks

- Trace each provider independently. A generic `syncProviderComments()` that only calls Instagram silently omits Facebook even when published Facebook targets have valid `platform_post_id` values.
- Resolve the provider target by either local post ID or exact target ID, require `PUBLISHED` plus a non-empty provider post ID, and verify ownership before token lookup.
- Instagram and Facebook use different Graph hosts and shapes:
  - Instagram top-level: `/{media-id}/comments`; replies: `/{comment-id}/replies`; fields include `text`, `username`, `timestamp`.
  - Facebook top-level and replies: `/{object-or-comment-id}/comments`; fields include `message`, `from`, `created_time`.
- Cursor-paginate top-level comments and each reply edge separately. Upsert the parent before its replies and preserve the existing local ID for a known provider comment ID.

## Async API and frontend contract

- Keep provider network sync asynchronous from GET so the cached local response returns immediately.
- While the drawer is open, fetch immediately, once shortly after sync starts, then lightly poll (about 10 seconds).
- Every refresh must load all local API pages before replacing UI state. Refreshing only offset 0 makes previously loaded older comments disappear and violates “all comments visible.” Prefer the API maximum page size and loop using `paging.hasMore`/`nextOffset`.
- Keep polling scoped to the mounted drawer. Clear timeout and interval on unmount.
- Auto-expand threads when replies exist so synchronized replies are clearly visible.

## Regression coverage

Backend:
- A post with published Instagram and Facebook targets causes requests to both Graph hosts.
- Cursor pagination persists multiple top-level pages and multiple reply pages.
- A local parent with an existing provider ID is reused rather than duplicated.

Frontend:
- A two-page API fixture renders comments from both pages simultaneously.
- A comment with replies renders reply text without requiring an expand click.

## Verification

From `apps/backend-go`:

```bash
gofmt -w internal/comments/*.go
go test ./internal/comments
go build -o /tmp/socialzen-api .
```

From `apps/frontend`:

```bash
pnpm exec vitest run src/components/comments/CommentList.test.tsx
pnpm typecheck
pnpm run build
```

Run verification after the final edit; an earlier passing build is stale evidence if source changed afterward.
