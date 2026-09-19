# Instagram Business Discovery confirmation and credential preflight

Use when a username-to-account flow must show the discovered Instagram account for confirmation before creating an identity or issuing a verification code.

## Contract

1. Username submit performs only a read-only Business Discovery search.
2. Render the returned profile identity and an explicit “Is this your account?” choice.
3. Before confirmation, assert no identity-creation/verification-code POST occurred.
4. On confirmation, submit the provider's stable user ID plus canonical username.
5. Server-side, repeat discovery and require both fields to match before creating the pending identity/code. This prevents stale or client-forged confirmation.
6. “No” clears the result and returns to search.

## Provider preflight

Before deployment, inspect the running service's effective dedicated-account ID and access token without printing secrets; record only presence, length, or a redacted fingerprint. Make a read-only request to the exact Graph version/account used by the service, URL-encoding:

`fields=business_discovery.username(<candidate>){id,username,name,profile_picture_url}`

Interpretation:

- `200` plus `business_discovery`: provider boundary is ready.
- `200` without it: valid empty result; render explicit no-match copy.
- OAuth error `190`, “Invalid OAuth access token - Cannot parse access token”: effective token is malformed, quoted incorrectly, truncated, or otherwise unusable. Replace it, restart, and rerun the public browser flow.
- Permission/account-type error: verify scopes, token ownership, professional-account eligibility, and the dedicated account.

Never expose the token in logs, shell output, screenshots, or reports.

## Verification and cleanup

Mocked provider tests prove the local contract only. Public authenticated E2E must render a real candidate and prove the create-request count is zero before confirmation. If the provider credential fails, report that exact boundary rather than promoting tests/build/health to READY.

If the browser creates temporary users, identify the live SQLite database from the running process or service config—not a similarly named repository DB. Delete only uniquely prefixed fixtures and run `PRAGMA integrity_check` afterward.
