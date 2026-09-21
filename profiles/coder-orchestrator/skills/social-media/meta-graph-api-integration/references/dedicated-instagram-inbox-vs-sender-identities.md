# Dedicated Instagram Inbox vs Sender Identities

Use this when an app receives Instagram DMs through one dedicated account and converts messages from other accounts into user-owned records.

## Keep the roles separate

- **Dedicated inbox:** the Instagram Professional account authorized by the access token. It is application integration configuration, not an app user's social identity.
- **Sender identity:** an Instagram account that DMs the dedicated inbox. It belongs in the user-identity flow only after verification from an inbound event.
- The access token authorizes operations on the inbox; it does not identify each message sender.
- For inbound events, match `recipient.id` to the configured inbox and use `sender.id` as the external user identity. Ignore self/echo messages.

## `/me` is not account search

`GET graph.instagram.com/{version}/me` returns the account that authorized the token. It cannot implement arbitrary Instagram username search. If the token belongs to `akun_testing911`, only that account can appear.

Never label `/me` as user search or place its result in a sender-account picker. Instead:

1. Expose the configured inbox separately in capability/settings data.
2. Mark username search unavailable unless a supported provider contract really performs discovery.
3. Register a normalized sender username as pending without pretending it has a stable provider ID.
4. Reject attempts to register the dedicated inbox as a sender.
5. Bind the stable sender ID only when the verification DM arrives through the webhook/event path.

## Minimal product correction

- Remove the misleading search route/client flow rather than retaining fake discovery.
- Render “Dedicated receiving inbox” separately from connected sender accounts.
- Let users enter the sender username, then instruct them to DM a one-time code to the inbox.
- Store `platform_user_id` as `NULL` while pending; populate it from the inbound DM sender ID upon successful verification.
- Preserve idempotency through the external message ID and reject events addressed to an unknown recipient.

## TDD regression matrix

1. Capability response has `search_enabled: false` and exposes the dedicated inbox separately.
2. The old search route is unavailable and does not call Meta.
3. Sender username registration creates a pending identity with no stable provider ID.
4. Registering the inbox username as a sender returns a conflict.
5. A verification DM addressed to the inbox binds its `sender.id` to the pending identity.
6. Subsequent DMs from that sender create notes; duplicate external message IDs do not.
7. UI contains no “searching” or account-confirmation copy and clearly distinguishes inbox from sender.

## Migration pitfall

When changing this contract, old tests may encode `/me` discovery and client-supplied provider IDs. Update fixtures narrowly to post sender usernames while preserving the broader verification, duplicate-message, recipient-isolation, and reply tests. Do not delete whole regression classes merely because their setup used the obsolete contract.
