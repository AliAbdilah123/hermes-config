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
See `references/instagram-insights-api.md` for the Instagram Insights endpoint (reach, impressions, saves).

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

## Threads Long-Lived Token Exchange

Threads short-lived tokens (1 hour) can be exchanged for long-lived tokens (default 14 days)
using the `th_exchange_token` grant type, identical in structure to Instagram and Facebook:

```
GET https://graph.threads.net/v1.0/access_token
  ?grant_type=th_exchange_token
  &access_token=<short-lived-token>
```

Response:
```json
{"access_token": "THQVJ...", "expires_in": 5184000}
```

```go
func (a *app) exchangeLongLivedThreadsToken(ctx context.Context, shortToken string) (string, time.Time, error) {
    q := url.Values{}
    q.Set("grant_type", "th_exchange_token")
    q.Set("access_token", shortToken)
    req, _ := http.NewRequestWithContext(ctx, http.MethodGet,
        fmt.Sprintf("%s/access_token?%s", threadsGraphBase, q.Encode()), nil)
    res, _ := a.config.HTTPClient.Do(req)
    defer res.Body.Close()
    // ... unmarshal access_token + expires_in ...
    expiresIn := out.ExpiresIn
    if expiresIn <= 0 { expiresIn = int64((14 * 24 * time.Hour).Seconds()) }
    return out.AccessToken, time.Now().UTC().Add(time.Duration(expiresIn) * time.Second), nil
}
```

Always attempt the long-lived exchange after obtaining the short-lived code-exchange token.
Fall back gracefully — the short-lived token still works for 1 hour.

## Threads Account Persistence

Threads OAuth accounts MUST be saved to the `threads_accounts` table, NOT `instagram_accounts`.
Sharing the `instagram_accounts` table causes Threads connections to appear as Instagram accounts
in dropdowns and causes token queries to fail (different schema, different Graph API base URL).

```go
// In oauthCallbackGeneric — before the instagram_accounts insert:
if cfg.Provider == "threads" {
    _, _ = a.db.Exec(`DELETE FROM threads_accounts WHERE user_id=? AND threads_user_id=?`, ...)
    _, err = a.db.Exec(
        `INSERT INTO threads_accounts (id,user_id,threads_user_id,threads_username,threads_name,profile_picture_url,access_token_encrypted,token_expires_at,status,created_at)
         VALUES (?,?,?,?,?,?,?,?,?,?)`, ...)
    // redirect on success
    return
}
```

The `threads_accounts` table schema:
```sql
CREATE TABLE threads_accounts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    threads_user_id TEXT NOT NULL,
    threads_username TEXT NOT NULL,
    threads_name TEXT,
    profile_picture_url TEXT,
    access_token_encrypted TEXT NOT NULL,
    token_expires_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at TEXT NOT NULL
);
```

## Post Targets: Cross-Platform Publishing Lifecycle

Posts have a parent `posts` row + child `post_targets` rows (one per platform).
The lifecycle:

```
SCHEDULED → enqueue (cron) → PUBLISHING → publish per-target → PUBLISHED
                                                        or  → FAILED (per-target)
```

**Enqueue** (cron, every 1 minute):
- Sets `posts.status='PUBLISHING'` where `status='SCHEDULED' AND publish_at<=now`
- Sets matching `post_targets.status='PUBLISHING'`

**Publish** (same cron cycle):
- Iterates PUBLISHING posts and their PUBLISHING targets
- Publishes each target independently
- On success: sets target to PUBLISHED with platform_post_id
- On failure: sets target to FAILED with error_message
- Parent post: PUBLISHED if ALL targets succeeded, FAILED otherwise (with descriptive message)

**Retry** (manual, via Edit & Retry in UI):
- Frontend opens edit form for FAILED posts (not just SCHEDULED)
- On save, PATCH handler resets: `posts.status='SCHEDULED'`, clears `error_message`
- Also resets FAILED `post_targets` to SCHEDULED (PUBLISHED targets stay PUBLISHED)
- Next cron cycle picks it up normally

Key gotcha: The backend PATCH for a FAILED post must reset status to SCHEDULED.
The frontend edit guard must allow `status === 'FAILED'` alongside `'SCHEDULED'`.

```go
// In PostByID PATCH handler:
res, _ := h.App.DB.Exec(`UPDATE posts SET status='SCHEDULED', error_message=NULL, updated_at=? WHERE id=? AND user_id=? AND status='FAILED'`, now, id, u.ID)
if n, _ := res.RowsAffected(); n > 0 {
    h.App.DB.Exec(`UPDATE post_targets SET status='SCHEDULED', error_message=NULL, updated_at=? WHERE post_id=? AND status='FAILED'`, now, id)
}
```

## Legacy post_targets Migration Pitfall

Migrations that add post_targets for ALL existing posts using `INSERT OR IGNORE ... SELECT FROM posts`
create **duplicate targets on every restart** if the target IDs don't match the IDs created by
the normal CreatePost flow. Example of a dangerous migration:

```sql
-- DANGEROUS: runs on every startup, creates duplicate instagram targets
INSERT OR IGNORE INTO post_targets (id,post_id,platform,account_id,status,created_at,updated_at)
SELECT 'pt_'||id,id,'instagram',instagram_account_id,status,created_at,updated_at FROM posts
```

If CreatePost generates random IDs like `pt_abc123` and the migration generates `pt_post123`,
`INSERT OR IGNORE` sees different IDs and inserts a **second** instagram target. This causes:
- Single-platform posts showing duplicate platform indicators
- Cross-platform posts getting an unwanted extra Instagram target
- Instagram posts being published twice

Fix: Remove once-off migrations after they've run, or use `id` that matches the CreatePost
ID generation scheme exactly.

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
