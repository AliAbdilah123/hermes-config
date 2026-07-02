---
name: meta-graph-api-integration
description: Meta Graph API (Facebook, Instagram, Threads) — token scopes, response quirks, publishing patterns, and common pitfalls.
---

Common patterns and gotchas when integrating with Meta's Graph API across Facebook, Instagram, and Threads platforms.

## Trigger

Use when debugging or implementing:
- Facebook/Instagram/Threads OAuth flows
- Cross-platform publishing (photos, videos, posts)
- Comment/like sync between local DB and Meta platforms
- Token/scope issues with Meta Graph API

See `references/error-transcripts.md` for raw error messages and reproduction recipes.

## Facebook OAuth Scopes

Publishing to Facebook Pages requires these minimum scopes:

```
pages_show_list
pages_read_engagement
pages_manage_posts
pages_manage_metadata
business_management
```

**Critical**: If you add new scopes, existing users MUST reconnect their Facebook account.
Old tokens don't carry the new permissions. The frontend should show a warning or
auto-prompt reconnection after scope changes.

## Instagram Publishing: Container Polling Required

Instagram's Graph API media publishing is a two-step process that requires polling:

1. **Create container** — POST to `/{ig-user-id}/media` with image/video URL
2. **Wait for container** — GET `/{container-id}?fields=status_code` until `FINISHED`
3. **Publish** — POST to `/{ig-user-id}/media_publish` with creation_id=containerID

The status codes: `IN_PROGRESS` → `FINISHED`, or `ERROR`/`EXPIRED`.

Without polling, you get error code 9007 subcode 2207027: "Media ID is not available."

```go
func waitForInstagramContainer(client *http.Client, graphVersion, igUserID, token, containerID string, timeout time.Duration) error {
    deadline := time.Now().Add(timeout)
    delay := 1 * time.Second
    for {
        if time.Now().After(deadline) {
            return fmt.Errorf("container not ready after %v", timeout)
        }
        statusURL := fmt.Sprintf("https://graph.instagram.com/%s/%s?fields=status_code&access_token=%s",
            graphVersion, containerID, url.QueryEscape(token))
        res, err := client.Get(statusURL)
        if err != nil { /* retry with backoff */ continue }
        var out struct{ StatusCode string `json:"status_code"` }
        json.NewDecoder(res.Body).Decode(&out)
        res.Body.Close()
        switch out.StatusCode {
        case "FINISHED": return nil
        case "ERROR", "EXPIRED": return fmt.Errorf("container status=%s", out.StatusCode)
        }
        time.Sleep(delay)
        delay = min(delay*1.5, 5*time.Second)
    }
}
```

## Threads API: user_id Is a Number

Threads token exchange (`POST graph.threads.net/oauth/access_token`) returns `user_id` as a JSON **number**, not a string:

```json
{"access_token": "THQVJ...", "user_id": 17841405793187218}
```

In Go, use `json.Number` — same pattern as Instagram:

```go
var tokenResp struct {
    AccessToken string      `json:"access_token"`
    UserID      json.Number `json:"user_id"`  // NOT string
}
```

Failure to handle this gives: `json: cannot unmarshal number into Go struct field .user_id of type string`

## Threads Graph API Base URL

The Threads Graph API requires a version in the base URL:

```
threadsGraphBase = "https://graph.threads.net/v1.0"
```

The `/me` endpoint works at `{base}/me` — without `/v1.0` it fails.

## Comment/Like Sync: DB Before API Race Condition

When syncing delete/unlike to Instagram, **query the API context (token, graph version, account) BEFORE deleting from the DB**, then pass those values to the goroutine:

```go
// WRONG — row is gone by the time goroutine runs
go h.tryDelete(localID, instagramID)  // re-queries DB, finds nothing

// RIGHT — capture context before DB mutation
if instagramID != "" {
    _, token, graphVersion, client, _ = h.instagramContext(localID)
}
// ... delete from DB ...
if instagramID != "" && token != "" {
    go h.tryDeleteWithToken(instagramID, token, graphVersion, client)
}
```

## Facebook Photo Publishing: published=true

Default for photo POST is `published=true`. Setting `published=false` uploads the photo but hides it from the feed — it's silent and confusing.

```go
// Correct:
q.Set("published", "true")  // or omit entirely (default is true)
```

## Facebook: pages_manage_posts Permission

Error `(#200) The permission(s) pages_manage_posts are not available` means:
- The app doesn't have `pages_manage_posts` in its OAuth scopes
- Or the user's token was obtained before the scope was added (needs reconnect)

For development mode apps, app admins/developers can use any permission without App Review.
For production, `pages_manage_posts` requires App Review.
