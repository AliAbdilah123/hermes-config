# Instagram Login Username Lookup

Use when a product with **Instagram Login** needs to validate a typed Instagram username without adding Facebook Login or Page credentials.

## Supported contract

Instagram Login does not provide arbitrary public-account discovery equivalent to Facebook Graph Business Discovery. Do not send an Instagram User access token to `graph.facebook.com/...business_discovery` and do not invent a public username-search endpoint.

Use the existing Instagram User token to fetch its owner:

```text
GET https://graph.instagram.com/<configured-version>/me
    ?fields=id,username,name,profile_picture_url
    &access_token=<instagram-user-token>
```

Normalize the typed username and provider username consistently. Return the provider account only on an exact normalized match; otherwise return `accounts: []`. This truthfully preserves a search → review → confirm UI, but limits lookup to the connected token-owner account.

## Configuration boundaries

- Keep one existing Instagram User token; do not add Facebook Login, Page tokens, or a second credential.
- Do not require or send the dedicated Instagram account ID for `/me`; retain that ID only where messaging/webhook routing independently needs it.
- Derive `search_enabled` from token presence, not an unrelated feature gate or account-ID field.
- Reuse the configured Graph version; do not scatter hardcoded versions.

## Error handling

Parse provider errors only enough to classify them. Never expose or log the token or raw provider body. Record sanitized HTTP status, provider type/code/subcode, then return stable application codes such as auth-invalid versus temporary-provider-failure. Map every returned code in the frontend so provider failures do not fall through to a generic unknown-error message.

## TDD and verification

Add contract tests first that prove:

1. Host/path is `graph.instagram.com/<version>/me`.
2. Requested fields are exactly the supported identity fields.
3. No `graph.facebook.com`, `business_discovery`, or dedicated account ID enters the lookup.
4. Exact normalized username returns one account; mismatch returns an empty array.
5. OAuth JSON and non-JSON failures become sanitized stable application errors.
6. `search_enabled` follows token availability.

Before deployment, make a non-destructive `/me` probe with the effective runtime token and report only HTTP status and non-secret identity metadata. Mocked tests establish request shape, not live-provider readiness. Finish with authenticated public search/confirm E2E before claiming completion.