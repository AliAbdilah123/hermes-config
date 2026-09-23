# Configured Instagram senders vs user social identities

Use when a dashboard confuses a dedicated inbox, application-configured sender accounts, and user-owned social identities.

## Keep the three roles separate

- **Dedicated inbox**: receives verification/note DMs and webhook events.
- **Configured sender**: an operator-provisioned account ID + access-token pair used by the application to send verification messages to the dedicated inbox.
- **User social identity**: a per-user pending/active record proven by a DM verification flow; it owns captured notes after activation.

Do not insert a configured sender into the user identity table merely to make it visible in Settings. That creates false ownership and bypasses verification. Instead, expose non-secret sender metadata from runtime configuration (normally username only) in an authenticated platform/settings response.

## Role-first inspection before destructive account edits

When a user asks what account/user is saved, or asks to clear a saved username and ID, do not infer the record's role from generic column names such as `username`, `user_id`, or `instagram_user_id`.

1. Identify the table and trace how the application reads it.
2. Classify the record as dedicated inbox, configured sender, or user social identity.
3. Report the role and ask for clarification if “user account” is ambiguous before deleting or blanking anything.
4. Check startup configuration: an `instagram_integrations` row may be restored from environment variables on restart, so direct database edits alone may be temporary or create env/DB drift.
5. For a dedicated inbox, derive the canonical account ID from that inbox token's `/me` response and keep its username, token, owner, and active status together. Never substitute an ID copied from webhook `entry.id`, a Facebook Page, another token, or an ordinary sender.
6. Clearing a dedicated inbox's username/ID disables receiver routing conceptually even if the token remains present; do not describe it as harmless “user data cleanup.”

A dedicated inbox belongs in `instagram_integrations`; ordinary connecting accounts belong in `social_identities`. Preserve this boundary during inspection, cleanup, restoration, and UI explanations.

## Diagnosis when “I can’t add this sender”

1. Trace the UI action. An “Add platform/account” flow may create a user identity, not manage the application sender pool.
2. Inspect whether an existing pending/active identity hides the one-account-per-platform add control.
3. Inspect effective sender credential pairs without printing tokens.
4. Validate each token non-destructively with `GET https://graph.instagram.com/me?fields=id,username,account_type` and require the returned ID to match the configured account ID.
5. If valid, add/persist only the sender's display metadata (for example `INSTAGRAM_USER2_USERNAME`) beside the existing ID/token pair and surface that metadata in the UI.
6. If the product truly needs runtime sender management, build an authenticated secret-management flow; do not overload user identity registration.

## Minimal response contract

```json
{
  "id": "instagram",
  "inbox": { "instagram_user_id": "...", "username": "dedicated_inbox" },
  "senders": [
    { "username": "sender_one" },
    { "username": "sender_two" }
  ]
}
```

Never return sender account IDs or access tokens unless a concrete client requirement justifies them. Usernames are sufficient for a settings label.

## Verification

- Regression: configured complete/distinct sender pairs appear in `senders`; incomplete pairs and the dedicated inbox do not.
- Provider preflight: `/me` confirms username, account type, and configured-ID match without logging secrets.
- Public authenticated Settings page visibly labels the section **Instagram sender** and lists the configured username(s).
- Treat source tests, bundle markers, and API health as supporting evidence; keep authenticated browser verification pending if the exact Settings page was not rendered.

## Polling terminology pitfall

Backend provider polling and frontend status refresh are different. “Webhook-only Instagram ingestion” means the server does not periodically query Meta for inbound DMs. A short-lived UI timer that refreshes the application's own identity-status endpoint after the user clicks “I've sent the code” does not poll Meta and can remain bounded to the waiting state.
