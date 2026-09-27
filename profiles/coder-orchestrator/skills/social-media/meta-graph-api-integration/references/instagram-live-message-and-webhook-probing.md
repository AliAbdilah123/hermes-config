# Instagram live message and webhook probing

Use when a user asks to send a real Instagram DM and then identify the resulting webhook IDs.

## Keep outbound delivery and inbound webhook tests separate

- An outbound `POST /me/messages` proves only that the token can address that recipient in its messaging namespace.
- It does **not** prove inbound webhook delivery or invoke the application's inbound `ProcessInstagramDM` path.
- To capture `sender.id`, `recipient.id`, and `message.mid` from an inbound webhook, have the real user account send a DM to the configured dedicated inbox while monitoring the receiver's logs.
- If outbound delivery returns Graph error `100`, subcode `2534014` (requested user not found), classify it as recipient/namespace/reachability failure. Do not infer webhook failure, and do not retry arbitrary IDs.

## Secret handling

- Never repeat an access token in output, logs, scripts, shell history, process arguments, or committed files.
- If a token is pasted into chat, treat it as compromised: recommend revocation/rotation and message deletion/redaction.
- Do not use an exposed token merely because the user later asks to send a message. Ask for a secure credential path or use an already-configured runtime integration that does not reveal the secret.
- Report only sanitized provider response fields: HTTP status, error code/subcode, message ID, recipient ID, and non-secret diagnostic text.

## Minimal evidence report

For the exact inbound event, report:

- raw `sender.id` (IGSID / messaging-scoped ID)
- raw `recipient.id`
- raw `message.mid`
- receiver-side `received_at`
- any requested exact-ID comparison as `true` or `false`
- whether `ProcessInstagramDM` was called, when relevant

Correlate every field from one fresh event boundary (timestamp/request trace). Query the receiver's debug endpoint only after provider acceptance and inbound arrival; confirm the running deployment actually exposes that route rather than inferring it from source code. If the endpoint requires authentication, use the established application session instead of weakening or bypassing auth.

If no event arrived in the stated window, report each raw field and comparison as unavailable—not `false`—and say processing was not observed. Never substitute configured IDs, public/profile IDs, outbound response IDs, an older webhook, or a dashboard/synthetic event.

## Exact-one live-send discipline

When asked to send exactly one real DM:

1. Resolve the sender credential pair and recipient ID without printing secrets.
2. Distinguish a public/profile Instagram user ID from the recipient's messaging-scoped ID; matching usernames do not make those IDs interchangeable.
3. Make at most one provider send request. Do not retry with guessed IDs after Graph error `100` / subcode `2534014`.
4. Call it a **send attempt** until Meta accepts it. A rejected POST means no real DM was sent and there can be no correlated inbound webhook.
5. After acceptance, wait for and correlate only a webhook received after the send timestamp, then query the debug endpoint and report its raw fields.
6. Do not use the Meta dashboard webhook test, a locally signed request, or existing logs as a substitute for the requested real DM.

A debug endpoint or full-body log may contain private message data. Read only the minimum fields requested and do not repeat message text, tokens, signatures, or unrelated payloads.
