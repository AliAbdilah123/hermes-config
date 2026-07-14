# Edit & Retry Save & Retry requeue implementation

Use this when failed SocialZen posts do not retry after pressing **Save & Retry**, especially when the user made no visible edits.

## Durable fix pattern

- Frontend `EditPostPage.tsx`: for `post.status === "FAILED"`, always include a retry intent in the PATCH body before the empty-body short-circuit:
  - `body.retry = true`
  - This prevents unchanged Save & Retry from only navigating away.
- Backend `internal/posts/handler.go`: keep retry requeue server-side and independent of changed visible fields:
  - reset matching failed parent post: `posts.status='SCHEDULED', error_message=NULL`
  - reset only failed targets: `post_targets.status='SCHEDULED', error_message=NULL`
  - preserve already `PUBLISHED` targets for partial-success posts.
- Backend PATCH should use key presence, not non-empty string checks, for editable fields:
  - `caption` key present with `""` means intentionally clear caption.
  - `media` key present with `[]` means intentional empty media input and must be handled/validated deliberately instead of silently keeping old rows.

## Regression tests to keep

Add/keep targeted backend tests under `apps/backend-go/internal/posts/`:

- failed post + failed Instagram target + published Facebook target + `{"retry": true}` PATCH helper call should produce:
  - post `SCHEDULED`
  - failed target `SCHEDULED`
  - published target still `PUBLISHED`
  - errors cleared
- scheduled post + `{"caption": ""}` should persist an empty caption.

A compact implementation is to extract the PATCH mutation into a small helper (for example `patchPost(uid, id, in, now)`) so the behavior can be tested without HTTP/session setup.

## Verification

```bash
cd /home/ubuntu/socialzen/apps/backend-go
go test ./internal/posts
go build -o /tmp/socialzen-api .

cd /home/ubuntu/socialzen/apps/frontend
pnpm typecheck
pnpm build
```

Deploy both backend and frontend, then verify the deployed EditPostPage JS asset returns `content-type: application/javascript` so Cloudflare/browser cache is not masking the new bundle.
