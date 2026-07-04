# Instagram Reel container timeout

## Trigger

Use when a SocialZen Reel/video uploads successfully but publishing later fails with an error like:

```text
Instagram media container not ready after 20s
```

This is a Meta media-container processing timeout, not an upload/crop failure by itself.

## Triage checklist

1. Confirm the file reached SocialZen storage and DB:
   ```bash
   sudo sqlite3 /opt/socialzen/data/socialzen.db "SELECT id,type,status,media_thumbnail,error_message FROM posts WHERE type IN ('REEL','VIDEO') ORDER BY updated_at DESC LIMIT 10;"
   sudo stat /opt/socialzen/data/media/<user>/<file>.mp4
   ```
2. Confirm OAuth/publisher basics before blaming scopes:
   - Instagram scopes include `instagram_business_content_publish`.
   - `createInstagramMediaContainer()` sends `media_type=REELS` and `video_url` for `REEL`/`VIDEO`.
   - The account has a non-empty `access_token_encrypted` and unexpired `token_expires_at`.
3. Check service logs for the exact failure:
   ```bash
   journalctl -u socialzen.service --since '24 hours ago' --no-pager | grep -Ei 'instagram|container|publish|reel|error'
   ```
4. If the failure is `container not ready after 20s`, increase video/Reel polling rather than changing scopes.

## Fix pattern

Keep image publishing fast, but allow videos/Reels longer Meta processing time:

```go
func instagramContainerTimeout(postType string) time.Duration {
    if postType == "REEL" || postType == "VIDEO" {
        return 3 * time.Minute
    }
    return 20 * time.Second
}
```

Then call:

```go
waitForInstagramContainer(client, graphVersion, igUserID, token, containerID, instagramContainerTimeout(post.typ))
```

Add a regression test that asserts `REEL` and `VIDEO` get at least 2 minutes while `PHOTO` remains 20 seconds.

## Verification

```bash
cd /home/ubuntu/socialzen/apps/backend-go
go test ./internal/posts -run TestInstagramContainerTimeoutByPostType -count=1
go test ./internal/posts ./internal/comments
go build -o /tmp/socialzen-api .
sudo install -m 755 /tmp/socialzen-api /opt/socialzen/socialzen-server
sudo systemctl restart socialzen.service
systemctl is-active socialzen.service
curl -s http://127.0.0.1:8089/health
```

If there is a known failed test Reel, reset only that post/target to `SCHEDULED` and let the cron retry. Verify it reaches `PUBLISHED` in `posts` and `post_targets`.

## Important distinction

Facebook Page failures mentioning `pages_manage_posts` are separate from Instagram Reel container timeouts. Do not add Facebook scopes to fix an Instagram Reel timeout. Facebook Page publishing needs Meta App Review/Advanced Access; requesting unapproved scopes can break OAuth connect entirely.
