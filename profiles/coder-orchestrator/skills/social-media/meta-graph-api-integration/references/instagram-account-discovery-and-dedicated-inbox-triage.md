# Instagram Account Discovery and Dedicated Inbox Triage

Use this when a product expects username autocomplete/profile-photo results or displays the wrong dedicated Instagram inbox during verification.

## Diagnose implementation before permissions

Trace the complete path before attributing failure to Meta scopes:

1. Check whether the frontend actually calls a search endpoint.
2. Check whether that backend route is registered and whether capability metadata explicitly disables search.
3. Search tests for assertions that the route must not exist; this often reveals an intentionally shipped prototype rather than a regression.
4. Inspect the handler for real HTTP calls to Meta. A local insert that accepts typed usernames is not account discovery.
5. Distinguish a real webhook from a simulated/test DM endpoint.

If no provider request exists, the root cause is missing implementation—not an Instagram Graph API vs Facebook Graph API or permission problem.

## Trace dedicated-account identity from runtime source

Do not assume a repository `.env` controls production:

1. Inspect the service unit for its actual `EnvironmentFile=` and `WorkingDirectory=`.
2. Check whether the config parser allowlists the needed keys. Strict parsers may reject newly added provider variables and prevent startup.
3. Inspect the running database for seeded integration rows. A migration may have inserted placeholder account ID/username values that every API response reuses.
4. Search frontend copy for hardcoded fallback usernames.
5. Compare, without exposing secrets: repository env, deployed service env, running process environment, database integration row, and API response.

A configured `INSTAGRAM_DEDICATED_ACCOUNT_ID` has no effect if the application never parses it, the service loads another env file, or responses come from seeded database data.

## API capability boundaries

- A known Instagram account ID can fetch that account's permitted fields when paired with a compatible access token and permissions.
- The ID does not grant arbitrary global username autocomplete.
- Business Discovery may inspect an eligible professional account by exact username, subject to account type, token, app mode, and approved permissions.
- Do not promise fuzzy people search or personal-account autocomplete unless an authoritative current Meta API contract explicitly supports it.

Prefer an exact-username verification UX when general discovery is unavailable. Only design a result list when the intended account class and API contract can actually supply stable IDs, usernames, and profile pictures.

## Minimal correction sequence

1. Add dedicated-account/token fields to the typed configuration and its allowlist.
2. Populate the actual deployed environment file.
3. Replace seeded placeholder integration data and UI fallbacks.
4. Resolve or validate the dedicated account through the appropriate Meta endpoint.
5. Implement the real webhook handshake/event path before claiming live DM verification.
6. Add regression checks for runtime config precedence, returned dedicated username/ID, and whether search is intentionally enabled or unavailable.
