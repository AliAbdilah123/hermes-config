# Meta/Facebook OAuth app-id and active-status debugging

Use this when a Facebook/Instagram connection fails with errors such as **Invalid App ID**, **App ID error**, or **App is not active**.

## Durable diagnostic pattern

1. **Verify the app is generating the expected OAuth URL**
   - Hit the app's OAuth start endpoint with a valid session cookie.
   - Parse the returned `authUrl`.
   - Check, without exposing secrets:
     - `client_id` length and last 4 digits
     - `redirect_uri`
     - Graph version path, e.g. `/v20.0/dialog/oauth`
     - requested scopes

2. **Compare env aliases and precedence**
   - Meta/Facebook OAuth usually needs the Meta/Facebook **App ID**, not an app secret and not a different Instagram/Threads app id.
   - Prefer app-id env names such as `META_APP_ID` / `FACEBOOK_APP_ID` / product-specific `INSTAGRAM_APP_ID` over stale legacy names like `INSTAGRAM_CLIENT_ID` when the latter may contain a secret-shaped value.
   - Compare values by length, last 4 digits, and hash prefix only; do not print secrets.

3. **Check redirect path drift**
   - In multi-project hosts, old env can point callbacks to a sibling project path.
   - Ensure `PUBLIC_BASE_URL`, `FRONTEND_BASE_URL`, and OAuth callback env vars all point to the current project path.

4. **Probe Facebook dialog behavior directly**
   - Use `curl -L` with a browser user-agent against the generated OAuth URL.
   - If the effective URL reaches `login.php` / dialog flow and the body does not contain `Invalid App ID`, the app id is structurally accepted.
   - If it redirects to `/oauth/error/?error_code=PLATFORM__INVALID_APP_ID`, the `client_id` is wrong for Facebook Login.

5. **Interpret “app is not active” separately**
   - This is normally a Meta app configuration/state issue, not an application-code bug.
   - Common causes:
     - App is still in Development mode.
     - The connecting Facebook user is not an administrator/developer/tester for the app.
     - Required product/permissions are not enabled or approved for public users.
   - With an app access token (`APP_ID|APP_SECRET`), verify app metadata/roles via Graph API when credentials are available.

## Verification checklist

- Backend tests covering env precedence pass.
- The deployed service was rebuilt/restarted and is active.
- Public OAuth start endpoint returns `status=configured` and a Facebook dialog URL.
- Generated OAuth URL contains the intended app id and project callback URL.
- Direct Facebook dialog probe no longer shows `Invalid App ID`; if it shows `app is not active`, hand off to Meta Developer Dashboard app-mode/roles configuration.
