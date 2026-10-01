# Facebook message history and ownership

Use this when adding a user-visible history of Facebook Messenger webhook events.

## Data contract

A receipt/deduplication table containing only message ID, Page ID, sender PSID, and timestamp cannot later render the message or its processing result. If product requirements include message history, persist—transactionally with processing:

- external message ID (deduplication key)
- sender PSID
- destination Page ID
- received timestamp
- message text
- terminal processing status (`note_created`, `activated`, `ignored`, `duplicate`, provider/application error as applicable)
- resulting note ID when one exists

Invalid-signature requests and malformed payloads must not be persisted. Never log message text, raw PSIDs, raw Page IDs, callback bodies, tokens, signatures, or secrets even when text is intentionally stored for the authenticated product UI.

## Ownership rule

A shared Page receives messages for multiple application users. Do not expose every Page receipt to every authenticated user.

The smallest safe user-scoping rule is to list receipts whose sender PSID matches that user's active Facebook social identity. This also makes earlier ignored/unverified receipts visible after that sender successfully connects, without leaking another sender's messages. If the product later adds a privileged operational inbox, implement explicit authorization rather than treating ordinary authentication as admin access.

## Transactional status updates

Insert the receipt before routing with a safe initial status, then update the same row inside the processing transaction:

- active sender and note insert succeed → `note_created` plus `note_id`
- verification succeeds → `activated`
- expired/invalid verification → matching terminal status
- no active or pending identity → `ignored`
- existing external message ID → report `duplicate` without overwriting the original terminal result unless the product explicitly models delivery attempts separately

Rollback must remove or restore the receipt consistently when processing fails; do not leave a receipt claiming success after note creation or activation rolled back.

## TDD and migration gates

1. RED: prove ignored messages are listable after sender connection and another sender's rows are excluded.
2. RED: prove the history endpoint requires authentication and returns text/status/note link fields.
3. GREEN: add the minimum schema, store query, endpoint, and table UI.
4. Test both clean bootstrap and upgrade of an existing database. Migration filenames must be unique; concurrent features commonly choose the same sequence number.
5. Back up and integrity-check the live SQLite database before deployment.
6. Authenticated browser E2E must cover an ignored message and a note-created message, origin/Page/status columns, note navigation, reload persistence, and cross-user isolation.

## UI

Reuse the existing Instagram/notes table visual system. Show received time, message, originating account, destination Page, status, and a note link when applicable. Include loading, error, and empty states. Raw IDs may be useful product data, but confirm whether full IDs or a masked presentation is appropriate for the intended user role.
