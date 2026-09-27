# Instagram Login webhook delivery triage

Use this when Instagram DMs appear in the Instagram app but do not reach an application using **Instagram Login** and Instagram User access tokens.

## Do not infer too much from provider responses

- `conversations: []` means only that the request was accepted and that query returned no visible conversations. It does not prove webhook delivery, complete permissions, correct app mode, or correct ID topology.
- A recipient-resolution error such as subcode `2534014` does not prove all scopes passed. Check whether the recipient is an Instagram-scoped messaging ID valid for the sending account/token context, rather than a profile/account ID copied from another context.
- A successful `/me` call narrowly proves that the token currently works for that endpoint. It does not prove the configured account ID matches the token or that the webhook callback works.
- The 24-hour messaging window mainly constrains business-initiated replies; it does not explain failure to ingest a fresh user-initiated inbound DM.
- Development/Live mode and integrity restrictions remain hypotheses until the local transport, callback, and IDs are proven correct.

## Transport-first investigation

1. Inspect source and the deployed binary for an actual webhook GET/POST route or polling worker. A simulated-DM endpoint is not an inbound Meta transport.
2. Probe the exact public callback path. SPA fallback HTML or `404` means Meta has no usable receiver.
3. Compare the ID returned by each token's `/me?fields=id,username,account_type` with the configured account ID. Do not print tokens.
4. Check `/me/subscribed_apps` for the `messages` field, but treat this as account-subscription evidence only; separately verify the Meta dashboard callback URL.
5. Inspect runtime DB/logs for provider message IDs, Instagram-sourced notes, and activated sender identities. No records plus no callback requests points to transport/configuration, not application dedupe.
6. Compare source commit, deployed binary timestamp/marker, running process, and nginx route. Git push is not deployment.

## Minimal secure callback contract

Expose one public path with:

- `GET`: require `hub.mode=subscribe`, exact nonempty `hub.verify_token`, and nonempty `hub.challenge`; compare the verify token in constant time and return the exact challenge as `text/plain`.
- `POST`: read the exact raw body with a size limit; require `X-Hub-Signature-256: sha256=<hex>`; validate HMAC-SHA256 with the Meta app secret before JSON parsing.
- Parse `entry[].messaging[]`; for text messages require `sender.id`, `recipient.id`, `message.mid`, and `message.text`.
- Ignore echoes, self-events, non-text events, and incomplete events.
- Feed webhook and simulation/polling transports through shared core identity/activation/note/reply logic, but keep transport-specific fallback policy explicit. Do not let a real-webhook fallback silently change simulated-endpoint behavior.
- For unmatched real DMs, never hardcode or configure sender usernames. Resolve fallback ownership from the dedicated inbox integration selected by the incoming `recipient.id` / configured dedicated account ID. Persist an owner foreign key on that integration record; a legacy owner email may populate the association at startup, but webhook delivery must not resolve ownership from email.
- Active sender identity takes precedence: save under that identity's owner. Only unmatched senders fall back to the dedicated integration owner.
- Deduplicate with the provider message ID. Return `200` promptly for valid signed payloads even when events are ignored or unmatched.
- Never log access tokens, app secrets, signatures, raw payloads, or message text.

## TDD and public verification matrix

Before implementation, add regressions for:

- valid challenge; wrong token/mode; missing configuration;
- valid signed empty payload;
- missing, malformed, and wrong signatures;
- malformed JSON after a valid signature;
- signed text event reaching activation/note processing;
- echo and non-text events ignored;
- no secret leakage.

After deployment verify independently:

1. local health on the exact systemd listener;
2. route marker in the exact `ExecStart` binary;
3. public challenge returns the exact supplied value;
4. the previously exposed/rotated token is rejected;
5. harmless signed empty payload returns `200`;
6. unsigned payload returns `403`;
7. Meta dashboard verification succeeds;
8. one fresh real DM produces a callback request and persisted note.

Do not call the work READY before step 8 when real inbound delivery is the acceptance criterion.

## Live receive-message test protocol

When the user asks whether a newly sent DM was received, distinguish **a webhook request** from **the requested real-message event**:

1. Record a baseline immediately before asking the user to send: current UTC time, latest webhook access-log timestamp, latest provider message ID, and latest persisted Instagram note.
2. Give the user a unique marker to send, then inspect only events newer than that baseline. Do not treat an older POST, a dashboard test, or an unrelated webhook as proof.
3. Verify all three layers independently:
   - nginx/public edge received a fresh Meta `POST`;
   - application logs classified it as a text message and report its processing outcome;
   - the expected database row exists, preferably matched by unique marker or provider message ID.
4. Query the live database used by the systemd process. Confirm the schema first (`PRAGMA table_info(...)` for SQLite) rather than guessing column names such as `content` versus `content_markdown`.
5. Avoid broad relative windows like “last 10 minutes” as the sole proof. Compare explicit timestamps/IDs against the captured baseline so an earlier event cannot be mistaken for the new test.
6. Report the narrowest supported result:
   - fresh POST + parsed + persisted: received successfully;
   - fresh POST but ignored/unmatched/not persisted: delivered, processing failed or routed incorrectly;
   - no fresh POST: Meta did not deliver the test to the callback;
   - uncertain timing/marker: inconclusive, repeat with a new unique marker.

A `200` response proves only that the callback accepted that request. It does not prove that the user's just-sent message arrived or was saved.

## Webhook-only cutover

When the user requires webhook-only ingestion, treat this as a runtime ownership change—not merely a longer polling interval:

1. Add a focused startup regression proving the server entry point does not launch the polling worker; observe it fail before changing production code.
2. Remove the poller launch and any startup-only options/logging it leaves unused. The polling implementation may remain as reusable/manual code unless deletion is explicitly requested.
3. Remove obsolete poll-interval configuration only when doing so will not make the strict environment loader reject a still-deployed legacy key. Coordinate config cleanup with deployment rather than breaking startup accidentally.
4. Run the focused regression, full backend tests, and a fresh build from the actual Go module root.
5. Replace the exact binary named by systemd, restart it, poll local health, and verify a marker from the poller startup path is absent from the deployed binary.
6. Probe the exact public webhook path with a deliberately wrong verification token and require `403`. This safely proves routing and webhook verification remain active without exposing secrets or fabricating a signed Meta event.
7. Do not claim real inbound delivery from the route probe alone. READY for a webhook-delivery acceptance criterion still requires one fresh real DM to arrive and persist.

Do not keep polling “as backup” after an explicit webhook-only decision. Conversely, do not delete shared DM processing logic used by both transports.

## Deployment/config pitfalls

- If a verify token was shown in chat or a screenshot, rotate it before enabling the callback and hand it off through a private server file or secret manager—not the same chat.
- A newly compiled binary may reject legacy `.env` keys that an older binary tolerated. Compare runtime keys against the loader whitelist before restart; preserve legitimate settings rather than deleting them blindly.
- Concurrent work may add polling while webhook work is being delivered. Fetch before push, inspect overlap, preserve both transports, and rerun their focused tests together before rebuilding the final binary.
- Build and deploy the integrated final commit, not a pre-rebase binary.
