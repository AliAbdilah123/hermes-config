# Text-only social webhook parity

Use this when a provider integration plan originally includes media but the user narrows the release to text-only while retaining shared note CRUD.

## Scope conversion

1. Convert the user’s correction into explicit behavior:
   - non-empty text creates one note;
   - text plus attachments creates one note containing only text;
   - attachment-only events create no note and persist no attachment metadata;
   - existing media support for other providers remains unchanged.
2. Mark media schema, parsing, rendering, and split-event correlation milestones as intentionally omitted—not blocked or partially implemented.
3. Do not require real media callback capture after the media scope is removed.
4. Add a regression for text-plus-attachment even when current code appears to discard attachments. If it passes immediately, record that the behavior already exists and avoid a no-op production edit.

## Shared note detail/edit proof

Provider ingestion success does not prove imported notes work in shared CRUD. Add an owner-scoped round trip:

1. Establish the social identity owner before delivering the webhook. Reassigning an identity afterward must not be expected to rewrite the note’s immutable `user_id`.
2. Deliver a signed provider text webhook.
3. Open the created note through the authenticated detail API/UI.
4. Edit title and content through the authenticated update API/UI with CSRF.
5. Reload and assert the edited values persist while `source` remains the provider.
6. Verify another user receives not-found for read/update/delete.

## Confirmation reply boundary

For a one-time post-verification reply:

- Claim the reply inside the same transaction that activates the identity, keyed by external message ID.
- Replays must not own another reply attempt.
- Send only after activation commits.
- Record `sent` or `system_failure`; outbound failure must not undo valid identity binding.
- Require the Page access token when the provider is configured; do not merely accept-and-ignore it.
- Preflight the effective runtime credential with a non-destructive provider request before deployment, redacting all token values.
- Distinguish an invalid token from missing provider permissions by recording only HTTP status, provider error code/subcode/type, and sanitized message.

## Public E2E fixture discipline

Use a unique temporary authenticated user and sender identity. Register cleanup before feature actions. Exercise the actual public callback and browser detail/edit routes, then delete the fixture and require both zero remaining fixture users and `PRAGMA integrity_check = ok`.

If live provider permission blocks only outbound confirmation, report that boundary separately from deployed text ingestion and authenticated CRUD evidence. Do not call real confirmation delivery verified until a genuine provider message succeeds.
