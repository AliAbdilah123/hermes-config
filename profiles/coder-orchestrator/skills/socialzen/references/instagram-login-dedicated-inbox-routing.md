# Instagram Login dedicated-inbox routing

Use this checklist when an Instagram DM webhook feeds a user-owned notes/inbox product.

## Architecture boundary

- Preserve **Instagram Login**. Do not silently migrate to Facebook Login, Page tokens, or Business Discovery.
- Keep the required scope set explicit and exact when the product contract requires only:
  - `instagram_business_basic`
  - `instagram_business_manage_messages`
- Validate declared scopes/configuration at startup without logging credentials. Reject unexpected Facebook/Page permissions rather than accepting a broader set accidentally.

## Account and token invariants

- Treat `INSTAGRAM_DEDICATED_ACCOUNT_ID` as the canonical inbox account ID.
- The dedicated account's Instagram access token is used for that account's Graph API polling/message operations. Per-identity sender tokens remain paired with their own Instagram account IDs.
- Validate each optional account-ID/token pair together. Never infer a token from a username or use a token belonging to another account.
- Sender usernames are runtime message metadata, not configuration. Never add observed senders to `.env`, seeds, or code.

## Webhook acceptance and routing

For a signed webhook payload:

1. Verify the signature with the Instagram app secret before parsing/processing.
2. Accept only `object=instagram`.
3. Require both the webhook entry ID and event recipient ID to equal `INSTAGRAM_DEDICATED_ACCOUNT_ID`; acknowledge and ignore events for other accounts.
4. Ignore echoes, empty text, missing message IDs, and self-sent events.
5. Resolve the sender against active Social Notes identities:
   - match: create the note for that identity's owner;
   - no match: create it for the owner configured on the dedicated inbox integration.
6. Resolve fallback ownership using the configured dedicated account ID, never the webhook-provided recipient as an unconstrained lookup key.
7. Preserve message-ID idempotency.

## Regression matrix

Add focused tests for:

- exact permission declaration accepted;
- missing or extra permissions rejected;
- required Instagram configuration present when integration values are supplied;
- optional account-ID/token pairs must be complete;
- active identity sender routes to its owner;
- unmatched sender routes to dedicated inbox owner;
- wrong object, entry ID, or recipient ID is acknowledged but creates no note;
- correct dedicated token is used for Graph API calls;
- duplicate external message ID creates no duplicate note.

Run focused package tests, the full backend suite, build, and `git diff --check` from the actual Go module root.

## Deployment and provider-backed E2E

- Add the exact non-secret permission declaration to the effective runtime env before restarting a binary that now validates it.
- Discover the service's actual listener and nginx prefix from systemd/nginx; do not assume a familiar port or health URL.
- Verify local health and the exact public prefixed health route separately.
- A signed synthetic webhook proves application routing, but not provider delivery. Final provider-backed acceptance requires a fresh DM from the named external test account, followed by database/API verification of message ID, note owner, and identity/fallback path.
- If the agent cannot originate that external account's DM, report the deployment as healthy but keep live DM E2E pending; ask the user to send the message and resume verification afterward.
