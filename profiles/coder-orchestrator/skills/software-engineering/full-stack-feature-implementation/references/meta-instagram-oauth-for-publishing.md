# Meta/Facebook OAuth for Instagram Publishing

Use this reference when a React/Vite + Go backend project says "Instagram connect" works in mock/degraded mode but real accounts still cannot connect for scheduling/publishing.

## Durable lesson

For third-party Instagram scheduling/publishing, do **not** wire only Instagram Basic Display OAuth (`https://api.instagram.com/oauth/authorize`, scopes like `user_profile,user_media`). Meta publishing flows require **Facebook Login + Facebook Graph API** because the app must discover the Facebook Page and its linked Instagram Professional account.

## Backend shape

- OAuth start should redirect to Facebook Login:
  - `https://www.facebook.com/{graphVersion}/dialog/oauth`
- Scopes should include the Page + Instagram permissions needed by the product, commonly:
  - `pages_show_list`
  - `pages_read_engagement`
  - `pages_manage_posts` — REQUIRED for Facebook Page publishing (feed, photos, videos)
  - `pages_manage_metadata` — needed alongside `pages_manage_posts` for full Page management
  - `instagram_basic`
  - `instagram_content_publish`
  - `business_management` when the app needs business/Page access discovery
- **Reconnect required**: Adding new scopes invalidates existing tokens. Users must disconnect/reconnect their Facebook account to get a token with the updated permissions. Without `pages_manage_posts`, Facebook publishing returns: `(#200) The permission(s) pages_manage_posts are not available`.
- `pages_manage_posts` and `pages_manage_metadata` require Facebook App Review for non-admin users. In development mode, app admins/developers/testers can use them without review.
- Exchange the callback `code` through Facebook Graph:
  - `GET https://graph.facebook.com/{graphVersion}/oauth/access_token?...`
- Discover Instagram accounts from the user’s Pages:
  - `GET https://graph.facebook.com/{graphVersion}/me/accounts?fields=id,name,access_token,instagram_business_account{id,username,profile_picture_url}`
- Save the `instagram_business_account` data as the connected publishing account.
- If no Page has an `instagram_business_account`, redirect to a user-facing error such as `no_ig_business_account` rather than returning a raw callback JSON error.

## Frontend/path pitfalls

- Callback redirects must match the frontend route/query handling. If the settings page expects `?tab=accounts&connected=1`, do not redirect to stale params like `?instagram=connected`.
- Login redirects in frontend helper functions should respect `import.meta.env.BASE_URL`; hardcoded `/login` breaks subpath deployments such as `/projects/brand-organizer/`.

## Env aliases that make deployments less brittle

Support both product-specific and Meta/Facebook key names where possible:

```text
INSTAGRAM_CLIENT_ID / META_APP_ID / FACEBOOK_APP_ID
INSTAGRAM_CLIENT_SECRET / META_APP_SECRET / FACEBOOK_APP_SECRET
INSTAGRAM_CONNECT_REDIRECT_URI / INSTAGRAM_REDIRECT_URI / FACEBOOK_REDIRECT_URI / META_REDIRECT_URI
FACEBOOK_GRAPH_VERSION / META_GRAPH_VERSION
OAUTH_STATE_SECRET
```

## Verification pattern

Add a backend test that configures fake app credentials and asserts `/api/instagram/connect/start` returns an auth URL containing:

- `https://www.facebook.com/{version}/dialog/oauth`
- `pages_show_list`
- `instagram_basic`
- `instagram_content_publish`

Then run the standard stack verification:

```bash
cd apps/backend-go && go test ./... && go build ./...
corepack pnpm --filter frontend typecheck
corepack pnpm --filter frontend build
```

Do not claim live deployment until the systemd binary/frontend webroot are actually replaced and the service is restarted/smoke-tested.

## Threads OAuth — `user_id` as JSON number

The Threads token exchange endpoint (`POST https://graph.threads.net/oauth/access_token`) returns `user_id` as a JSON **number** (e.g., `17841405793187218`), not a string:

```json
{"access_token": "THQVJ...", "user_id": 17841405793187218}
```

This is the same quirk Instagram Login OAuth has — the Meta API returns numeric `user_id` on multiple endpoints. Use `json.Number` in the Go struct to handle both:

```go
var tokenResp struct {
    AccessToken string      `json:"access_token"`
    UserID      json.Number `json:"user_id"`
}
// ...
userID := tokenResp.UserID.String()
```

Using `string` for `user_id` causes:
```
json: cannot unmarshal number into Go struct field .user_id of type string
```

**Pitfall**: If Instagram token exchange already handles this with `json.Number` but Threads exchange was copy-pasted with `string`, the bug silently survives until someone actually connects a Threads account. Always check both paths when adding a new Meta platform.

Also ensure the Threads Graph API base URL includes the API version:
```go
threadsGraphBase = "https://graph.threads.net/v1.0"  // NOT "https://graph.threads.net"
```

## Threads long-lived token exchange

Threads short-lived tokens are valid for 1 hour. Exchange them for long-lived tokens using the `th_exchange_token` grant type, same pattern as Instagram (`ig_exchange_token`) and Facebook (`fb_exchange_token`):

```go
func (a *app) exchangeLongLivedThreadsToken(ctx context.Context, shortToken string) (string, time.Time, error) {
    q := url.Values{}
    q.Set("grant_type", "th_exchange_token")
    q.Set("access_token", shortToken)
    req, _ := http.NewRequestWithContext(ctx, http.MethodGet,
        fmt.Sprintf("%s/access_token?%s", threadsGraphBase, q.Encode()), nil)
    // ... parse {access_token, expires_in} from response
    return out.AccessToken, time.Now().UTC().Add(time.Duration(expiresIn) * time.Second), nil
}
```

Call this after the initial code exchange, before saving. Fall back to 14-day default expiry if the exchange fails. Store the resulting long-lived token and expiry in `threads_accounts.access_token_encrypted` and `token_expires_at`.

**Pitfall**: Without long-lived exchange, the Threads token expires in 1 hour while Instagram/Facebook tokens last ~60 days. The user's Threads connection stops working almost immediately, requiring a reconnect every session.
