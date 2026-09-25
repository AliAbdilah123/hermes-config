# Instagram subscription and Meta App identity cross-check

Use this for a **read-only** investigation when an Instagram Login account returns a numeric `subscribed_apps.data[].id` and someone needs to know whether it is the Meta Developer App ID.

## Core rule

Do **not** label `/{ig-user-id}/subscribed_apps.data[].id` as the Meta Developer App ID merely because the edge is named `subscribed_apps`. Treat it as a subscription-associated identifier until independently correlated with the app ID from credentials, token metadata, or the Meta App Dashboard.

Instagram Login commonly exposes several distinct identifiers:

- configured OAuth client / Meta App ID (`INSTAGRAM_APP_ID`);
- Instagram Login account ID from `/me.id`;
- Instagram user ID from `/me.user_id`;
- `subscribed_apps.data[].id` returned for that account;
- Facebook/Instagram business asset IDs in other API contexts.

Never merge these namespaces by numeric appearance.

## Minimal read-only procedure

1. Read the deployed configuration without printing secrets. Record only the configured app ID, account IDs/usernames, and whether credentials exist.
2. For each available Instagram user token, call:
   - `GET https://graph.instagram.com/me?fields=id,user_id,username,account_type`
   - `GET https://graph.instagram.com/me/subscribed_apps`
3. Record, per token: username, `/me.id`, `/me.user_id`, subscription `id`, and `subscribed_fields`.
4. Attempt token provenance independently using Meta's supported token-inspection mechanism and an app access token derived from the corresponding app credentials. Redact all tokens and secrets.
5. Correlate the configured app ID with the exact App Dashboard entry/name. Dashboard confirmation is the fallback when token inspection does not support that Instagram token type.
6. Compare accounts using separate conclusions:
   - same/different **subscription-associated IDs**;
   - same/different **proven Meta Developer App IDs**.

## Evidence discipline

- Different `subscribed_apps.data[].id` values prove different returned subscription contexts, not necessarily different Meta Developer Apps.
- A configured app ID is strong deployment evidence, but it does not by itself prove that an already-issued token came from that app.
- `/me` proves token-to-account identity only for that endpoint.
- Failed `/debug_token` or object lookup is inconclusive; do not reinterpret the returned subscription ID as an app ID to fill the gap.
- If app provenance cannot be independently verified, state **likely/configured** versus **API-verified** explicitly.
- The decisive result should answer whether both accounts share a proven app context, while preserving uncertainty if only subscription identifiers differ.

## Safe reporting table

| Account | `/me.id` | `/me.user_id` | `subscribed_apps[].id` | Fields | Proven Meta App ID |
|---|---:|---:|---:|---|---:|

Keep the final concise: exact observations, what each identifier means, same-app verdict, and the one remaining dashboard/API check if unresolved. Never print access tokens, app secrets, app access tokens, or raw secret-bearing environment lines.
