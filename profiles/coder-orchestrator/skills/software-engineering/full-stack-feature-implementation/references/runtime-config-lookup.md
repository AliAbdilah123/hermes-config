# Runtime config lookup without leaking secrets

Use this pattern when a user asks which app/client ID, redirect URI, feature flag, or other runtime config value a deployed full-stack project is using.

## Pattern

1. Identify the runtime process/service definition rather than assuming repository `.env` is authoritative.
   - For systemd deployments: inspect `systemctl cat <service>` or `systemctl show <service> -p Environment -p EnvironmentFiles`.
   - Note `Environment=...`, `EnvironmentFile=...`, `WorkingDirectory=...`, and `ExecStart=...`.
2. Inspect application config-loading code to understand aliases/fallbacks.
   - Example: one Go backend loaded `InstagramClientID` from the first present of `INSTAGRAM_CLIENT_ID`, `META_APP_ID`, or `FACEBOOK_APP_ID`, so a single Meta app/client ID applied to both Instagram and Facebook OAuth aliases.
3. Extract only explicitly non-secret values.
   - Allowlist identifiers and public config such as `*_APP_ID`, `*_CLIENT_ID`, redirect URIs, graph versions, public base URLs.
   - Never print or summarize `*_SECRET`, `*_KEY`, tokens, passwords, cookies, encryption keys, or raw secret-bearing `.env` contents.
   - Prefer small allowlisted commands/scripts over dumping files.
4. Verify runtime behavior when there is a safe endpoint.
   - Example: call a config/status endpoint that reports `configured: true` and public redirect URI, or inspect generated OAuth start URL for the expected host/scopes without exposing secrets.
5. Answer directly and name the source of truth.
   - State whether the value came from the live service env, repo template, or config code fallback.
   - If repo `.env` and deployed service env differ, prioritize the deployed service for “what is used” questions and mention the distinction.

## Example safe extraction command

```bash
sudo -n sh -c "grep -E '^(INSTAGRAM_CLIENT_ID|META_APP_ID|FACEBOOK_APP_ID|INSTAGRAM_APP_ID|INSTAGRAM_REDIRECT_URI|FACEBOOK_REDIRECT_URI|META_REDIRECT_URI|FACEBOOK_GRAPH_VERSION)=' /var/lib/brand-organizer/.env" 2>/dev/null || true
```

Adjust the allowlist for the project. Do not broaden to secrets.
