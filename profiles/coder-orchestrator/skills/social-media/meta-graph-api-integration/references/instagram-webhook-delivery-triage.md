# Instagram webhook delivery triage

Use this when Instagram Login webhook verification succeeds but inbound DMs do not appear in the application.

## Trace boundaries in order

1. **Meta → edge:** inspect access logs for a fresh `facebookexternalua` POST to the exact callback and record timestamp/status. A `200` proves delivery and signature acceptance only—not event processing or persistence.
2. **Payload → parser:** safely record metadata only (event kind, entry count, whether sender/recipient/message IDs and text are present). Never log message text, raw payloads, signatures, tokens, or app secrets. Compare real payload shape against test fixtures.
3. **Identity namespace:** for every access token, call its own `/me?fields=id,username` and compare that ID to the account ID configured with that token. Never mix copied IDs across tokens/apps. A stale recipient ID can cause valid events to be classified as unmatched while the webhook still returns `200`.
4. **Processing outcome:** distinguish activated/known sender, unmatched sender, ignored echo/non-text, duplicate message ID, and storage error. Do not silently discard unmatched DMs if the product promises a general inbox; use the same fallback persistence behavior as polling.
5. **Persistence:** query by external message ID and source. Verify exactly one row, expected owner, and deduplication. HTTP success is not E2E success.
6. **Provider read APIs:** `conversations: []` means only that the request succeeded and returned no visible conversations in that context. It does not prove all permissions, dev/live visibility, webhook delivery, or correct ID namespace.

## Configuration and deployment

- `.env` edits do not affect a running systemd process until restart. Verify the unit's `EnvironmentFile`, restart, then inspect running health and loaded non-secret identity suffixes.
- Meta callback GET must return the exact challenge. POST must validate `X-Hub-Signature-256` over exact raw bytes with the app secret.
- The webhook verify token is a shared setup secret; never commit it. If the operator lacks server access, use an approved secure handoff—not a public chat or repository—and rotate any exposed token.
- Test with one unique, fresh, text-only DM after deployment. READY requires access-log delivery plus the expected database/application result.

## Common misleading conclusions

- `200` webhook response ≠ message saved.
- Error subcode `2534014` does not uniquely prove permissions passed or that dev-mode thread visibility is the cause.
- A valid `/me` response establishes narrow token validity, not webhook subscription correctness.
- The 24-hour messaging window mainly limits business-initiated replies; it does not explain failure to ingest a fresh user-initiated inbound DM.
