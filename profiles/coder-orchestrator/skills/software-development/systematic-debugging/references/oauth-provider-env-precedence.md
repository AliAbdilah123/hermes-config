# OAuth provider env precedence debugging

Use this when a social login/OAuth flow reports an "Invalid App ID", "app id error", or lands on the provider error page even though the user says env vars were updated.

## Pattern observed

A deployed app can still generate a bad provider authorize URL when multiple legacy env var names exist for the same concept. In one SocialZen-style Facebook/Instagram Graph OAuth flow:

- `INSTAGRAM_CLIENT_ID` contained a stale 32-character secret-shaped value.
- `META_APP_ID` contained the real 16-digit Meta/Facebook app id.
- Backend config loaded `INSTAGRAM_CLIENT_ID` before `META_APP_ID`, so Facebook received the wrong `client_id` and rejected the OAuth dialog.
- Redirect URI envs also still pointed to a previous project path, causing callback/cancel URLs to reference the wrong app.

## Investigation recipe

1. Inspect the running service env, not only repository env files. For systemd services, use `systemctl cat <service>` to find `EnvironmentFile=` and compare masked key names with `/proc/<pid>/environ`.
2. Generate the OAuth start URL from the deployed endpoint using a real session cookie if needed.
3. Parse the authorize URL, but do not print secrets. Record safe facts only:
   - authorize host/path
   - `client_id` length and last 4 chars
   - `redirect_uri`
   - scopes
4. Fetch the provider dialog URL with redirects enabled and a browser-like user agent. Verify whether the response contains the provider's invalid-app-id text or reaches login/oauth flow.
5. Check for stale project-path redirects such as `/projects/old-app/...` in `redirect_uri`, `cancel_url`, or frontend base URLs.

## Durable fix pattern

- Prefer canonical provider app id envs over legacy product-specific aliases, e.g. for Meta/Facebook OAuth prefer `META_APP_ID` / `FACEBOOK_APP_ID` / `INSTAGRAM_APP_ID` before a stale `INSTAGRAM_CLIENT_ID` alias.
- Keep secrets separate from IDs. Do not allow `*_SECRET`, `*_SECRET_ID`, or secret-shaped values to act as `client_id`.
- Do not let unconfigured OAuth providers return a local/mock settings success URL from production endpoints. That masks missing `client_id`/`redirect_uri` as “button bounced back to Settings.” Return an explicit non-2xx `OAUTH_NOT_CONFIGURED`-style API error and make the frontend show a clear message instead of redirecting.
- Add regression tests for both precedence and unconfigured-provider behavior: with missing app id/redirect URI, the start endpoint must fail explicitly and must not include the provider success redirect as `authUrl`.
- Update deployment env redirect URIs to the current public project path and restart the running service.
- Verify end-to-end by checking both the local service endpoint and the public routed endpoint.

## Verification example shape

- Backend unit tests pass.
- Service is active after restart.
- `/api/.../oauth/start` returns an auth URL whose `client_id` is the canonical app id and whose `redirect_uri` matches the current app path.
- Provider dialog fetch no longer contains "Invalid App ID" and redirects to the provider login/oauth page.
