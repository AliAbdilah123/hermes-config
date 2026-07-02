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

**Caveat**: `pages_manage_posts` and `pages_manage_metadata` require **Facebook Login for Business**
(business-type app + Advanced Access). Requesting them on a regular consumer Facebook Login
app makes Meta **reject the entire OAuth dialog** with "Invalid Scopes". For consumer apps,
limit scopes to `pages_show_list`, `pages_read_engagement`, `business_management` and handle
publishing through Instagram (direct) or get the app converted to Business type.

For development mode apps, app admins/developers can use any permission without App Review.
For production, `pages_manage_posts` requires App Review.

## Account Provider Tags

When integrating Facebook, Instagram, and Threads OAuth, the same real-world account can
arrive through different connection flows. Tag each account with a `provider` column:

| Provider    | Source                                          | Token Available? |
|-------------|-------------------------------------------------|------------------|
| `instagram` | Direct Instagram OAuth (Instagram Login)        | ✅ Full token    |
| `facebook`  | Facebook Login → linked IG Business Account     | ⚠️ May be empty  |
| `threads`   | Direct Threads OAuth                            | ✅ Full token    |
| `mock`      | Demo/seed data                                  | N/A              |

**Pitfall**: Facebook-linked IG Business Accounts (provider=`facebook`) often end up with
no `access_token_encrypted` because the Facebook OAuth flow returns a Facebook Page token,
not an Instagram token. The publisher/business logic must handle this gracefully.

**Publisher query pattern**: When querying accounts for Instagram publishing, accept both
`provider='instagram'` and `provider='facebook'` since both can publish via the Instagram
Graph API, but check for non-empty tokens:

```sql
SELECT ig_user_id, access_token_encrypted, token_expires_at
FROM instagram_accounts
WHERE id=? AND user_id=?
  AND (provider='instagram' OR provider='facebook')
```

**Frontend label format**: Use `@username : Platform` (colon separator) for all account
selectors — CreatePost dropdowns, Settings account cards, etc. Facebook-linked accounts
get `: via Facebook`, direct Instagram gets `: Instagram`, Threads gets `: Threads`.

```tsx
// CreatePost account dropdown
accounts.filter(a => provider === "instagram" || provider === "mock" || provider === "facebook").map(a => (
  <SelectItem value={a.id}>
    @{a.igUsername} : {a.provider === 'facebook' ? 'via Facebook' : 'Instagram'}
  </SelectItem>
))
```

**SocialZen architecture note**: Facebook OAuth callback (instagram_oauth.go ~line 567)
intentionally does NOT insert `instagram_accounts` rows for Instagram Business Accounts
discovered via Facebook Pages. The comment reads: "Facebook-linked Instagram accounts
are deliberately not inserted here. Users must connect Instagram explicitly with the
Instagram button." Facebook flow only populates the `facebook_pages` table. Any
`instagram_accounts` rows with `provider='facebook'` are leftovers from an older code
path that has since been removed.

## access_token_encrypted Column

The `access_token_encrypted` column is often added via **ALTER TABLE migration** after the
initial CREATE TABLE. The migration pattern (safe for re-runs):

```sql
ALTER TABLE instagram_accounts ADD COLUMN access_token_encrypted TEXT;
```

Wrap in error handling that ignores "duplicate column" errors:

```go
if _, err := db.Exec(`ALTER TABLE instagram_accounts ADD COLUMN access_token_encrypted TEXT`); err != nil {
    if !strings.Contains(strings.ToLower(err.Error()), "duplicate column") {
        return err
    }
}
```

Verify the column exists before deploying publisher code that queries it — missing column
produces silent scan failures that look like "account not connected" errors.
