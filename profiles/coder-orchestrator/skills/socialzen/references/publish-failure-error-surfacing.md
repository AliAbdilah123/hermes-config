# Publish failure error surfacing

When a failed post shows only a generic parent error such as `Some platforms failed to publish`, inspect the publishing pipeline before changing frontend copy.

## Root cause pattern

`PublishDuePosts()` writes detailed per-target errors to `post_targets.error_message`, then may overwrite the parent `posts.error_message` with a generic aggregate string. The UI (`PostCard`) displays `post.errorMessage`, so users never see the real platform-specific cause.

## Fix pattern

- Keep the per-target error writes unchanged.
- When setting the parent post to `FAILED`, aggregate failed target rows:
  - query `post_targets` for `status='FAILED'`
  - format each as `<Platform> failed: <error_message>`
  - use `Could not publish: ...` when no target succeeded
  - use `Partially published: ...` when some targets are already `PUBLISHED`
- Keep fallback generic messages only for DB/query failure or zero failed target rows.

Example parent error:

```text
Could not publish: Instagram failed: Instagram account not connected for publishing; reconnect Instagram; Facebook failed: Facebook page page_1 not found or expired
```

## Regression test shape

Add/keep a small `internal/posts` test that inserts failed `post_targets` with platform-specific `error_message` values and asserts the aggregate parent message contains those exact reasons in target order.

## Verification

```bash
cd apps/backend-go
gofmt -w internal/posts/publisher.go internal/posts/publisher_test.go
go test ./internal/posts
go build -o /tmp/socialzen-api .
```

Deploy backend only if frontend did not change:

```bash
sudo install -m 755 /tmp/socialzen-api /opt/socialzen/socialzen-server
sudo systemctl restart socialzen.service
systemctl is-active socialzen.service
curl -sS http://127.0.0.1:8089/health
```
