# Social Publishing + OAuth Triage

Use when a social scheduler reports published posts that do not appear on Facebook/Instagram, account-connect state is wrong, or reconnect/disconnect UX is misleading.

## Durable checks

1. Trace publish status transitions before fixing UI.
   - Search for handlers or polling/read paths that mutate `SCHEDULED`/`PUBLISHING` to `PUBLISHED` without a provider API response.
   - Parent post status is not enough; inspect per-platform target rows (`post_targets` or equivalent).
   - Billing/quota should count only provider-confirmed publish successes.

2. Verify required publish credentials are actually persisted.
   - Facebook Page publishing needs the external `page_id` and page access token, not the internal DB row id.
   - Instagram image publishing needs IG user id + stored access token, then the Graph media-container flow:
     - `POST /{ig_user_id}/media` with `image_url`, `caption`, `access_token`.
     - `POST /{ig_user_id}/media_publish` with `creation_id`, `access_token`.
     - Mark published only after the returned media id exists.
   - If token storage was added after users connected accounts, old rows may need reconnect; do not fake success for tokenless rows.

3. Keep provider account models separate unless product explicitly asks for cross-linking.
   - Facebook Pages can expose `instagram_business_account`, but if the UI has separate direct Instagram connect, do not auto-create direct Instagram accounts from Facebook connect.
   - Historical bad rows (for example provider=`facebook` inside an Instagram accounts table) can trigger stale reconnect banners even after direct Instagram reconnect. Filter banners/UX by real provider and clean unused bad rows only after checking references.
   - **Frontend account-list over-filtering pitfall:** when the UI filters accounts by `provider === "instagram"`, any Facebook-linked accounts (provider=`facebook`) become INVISIBLE — users see "No accounts connected" even though they connected Facebook. Fix: include `provider === "facebook"` in the filter and label them as "· via Facebook" so users can see, identify, and know they need direct Instagram reconnect. Apply the same fix to CreatePost account dropdowns.

4. OAuth URL/provider-flow checks.
   - Parse generated OAuth URLs: host/path, `client_id`, `redirect_uri`, scopes, state, and provider-specific params.
   - **Facebook scope enforcement pitfall:** Meta rejects the OAuth dialog with `"Invalid Scopes: pages_manage_posts, pages_manage_metadata"` unless the app is a Business-type app with Advanced Access. If your app is a regular Login app, remove these scopes from the request array so users can at least connect with `pages_show_list`, `pages_read_engagement`, and `business_management`. Add them back only after completing Facebook App Review for Business Login.
   - For Meta/Facebook Business Login, a normal `/dialog/oauth` may drop users into an already-authenticated Facebook/social experience. Force permission/login dialog with params such as `auth_type=rerequest`, `display=popup`, `enable_profile_selector=1` and support a dashboard-provided Business Login `config_id` (commonly exposed as `FACEBOOK_LOGIN_CONFIG_ID`/`FACEBOOK_CONFIG_ID`). Without the config id, code can force a permission dialog but cannot guarantee the exact Business onboarding screen.
   - For Instagram long-lived tokens, exchange the short token (`grant_type=ig_exchange_token`) and store the provider's actual expiry; use a safe fallback only for UI expiry, not as proof the provider token is valid.

5. Reconnect/disconnect UX pitfalls.
   - A request to “add disconnect” can mean “always let me disconnect, even when expired.” Do not replace disconnect with reconnect for expired accounts; offer reconnect via the add/connect button or a separate action.
   - Reconnect warning banners should ignore mock/demo accounts and other providers unless the banner is explicitly multi-provider.

## Verification pattern

- Run the narrow backend publisher tests or add one if absent.
- Build the backend and frontend artifacts that are actually deployed.
- Restart the service, verify health, and confirm DB migrations/columns with a read-only schema probe.
- Fetch public domain and path-based URLs if both are deployed.
- If cleaning stale account rows, first count rows referenced by posts/targets; delete only unreferenced stale rows.
