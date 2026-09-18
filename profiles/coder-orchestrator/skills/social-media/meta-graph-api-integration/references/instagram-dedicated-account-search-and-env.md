# Instagram dedicated-account search and runtime configuration

Use this when an app lets users identify an Instagram account, shows a dedicated inbox account for DM verification, or claims to search Instagram usernames.

## Separate the three identities

1. **Dedicated receiver account** — the professional Instagram account that receives verification DMs. Its stable ID and displayed username must come from effective runtime configuration, not seed/migration placeholders.
2. **Candidate user account** — the username the user wants to register.
3. **Meta application** — app ID/secret identify the application; they are not an Instagram user/Page access token.

Do not use a seeded ID such as `17841400000000000` or a UI fallback username after real configuration exists. Upsert/synchronize the singleton integration row at startup from the effective config so existing databases are repaired without rewriting an already-applied migration.

## Search capability boundary

Meta does not provide unrestricted fuzzy autocomplete over arbitrary Instagram personal accounts. For eligible professional accounts, use exact-username **Business Discovery** through the Facebook Graph API:

```text
GET https://graph.facebook.com/<version>/<DEDICATED_IG_USER_ID>
  ?fields=business_discovery.username(<exact_username>){id,username,name,profile_picture_url}
  &access_token=<USER_OR_PAGE_ACCESS_TOKEN>
```

Return a list-shaped response to the UI even though exact lookup normally yields zero or one result. Never fabricate matching accounts when credentials are absent. Return a clear unavailable state and explain that the app ID and app secret cannot substitute for a user/Page access token.

## Configuration and service source of truth

Before debugging scopes or API hosts:

1. Inspect the service's actual startup command (`ExecStart`) and env-file argument.
2. Compare that path with the env file the user expects the app to use.
3. Confirm the application's config allowlist accepts every required key; switching the service to a richer `.env` can otherwise make strict config parsing reject startup.
4. Pass configuration through `main -> HTTP options/service -> store/API client`; merely placing keys in `.env` does not wire behavior.
5. Avoid logging access tokens, app secrets, and webhook verify tokens.

Typical keys:

```env
INSTAGRAM_APP_ID=...
INSTAGRAM_APP_SECRET=...
INSTAGRAM_DEDICATED_ACCOUNT_ID=...
INSTAGRAM_DEDICATED_USERNAME=...
INSTAGRAM_ACCESS_TOKEN=...
INSTAGRAM_WEBHOOK_VERIFY_TOKEN=...
```

The exact names may differ by project; prefer the project's canonical names and avoid aliases unless compatibility requires them.

## Verification matrix

- Config test accepts and exposes the dedicated ID, username, and token without printing secrets.
- Existing database startup synchronization replaces placeholder ID/username.
- Verification-code create and regenerate responses identify the configured dedicated account.
- Authenticated search without a token returns an explicit unavailable error.
- Search with a stub HTTP client verifies the Graph host, dedicated account path, exact username field, and maps ID/username/name/profile photo.
- UI test verifies request encoding, result rendering, and removal of hardcoded fallback usernames.
- Deployed service proves it reads the intended env path, health is ready, and the runtime integration row contains the configured ID/username.
- Public authenticated flow verifies search behavior and verification-code account identity; clean temporary users afterward and run SQLite integrity checks when applicable.
