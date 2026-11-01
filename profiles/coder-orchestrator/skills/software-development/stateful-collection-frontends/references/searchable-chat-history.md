# Searchable chat-history collections

Use this pattern when an existing single-thread chat UI gains multiple durable threads, search, infinite scroll, and thread restoration.

## Inspect before planning

Trace the full data path before drawing the history UI:

- Does the database store transcripts, or only an upstream session ID?
- Are assistant responses durable or held only in process memory?
- Does “New chat” create immediately or on first send?
- Can old threads be reconstructed after restart?
- Which project/tenant/account scopes every list and detail query?
- Which upstream session ID must be reused when reopening a thread?

A history/search UI is not frontend-only when message text is not persisted locally. State this contract change explicitly rather than implying search can query unavailable history.

## Minimal durable model

Prefer the existing relational store:

- Add a conversation title derived from the normalized first user message; avoid an extra AI title call unless explicitly requested.
- Add ordered user/assistant message rows linked to the conversation.
- Update the conversation timestamp after every successfully persisted turn.
- Index scope plus `(updated_at, id)` and message foreign key plus ID.
- Use native full-text search when already available; otherwise keep the fallback in the same database rather than adding a search service prematurely.

Persist only real successful assistant output. Never manufacture transcript content from a generic completion event. On upstream failure, preserve retryable user input in the client without storing a fake assistant turn.

## New-thread semantics

Route every New chat entry point through one reset function that clears:

- active conversation identity,
- rendered messages,
- upstream session status,
- stale attached context,
- history/detail loading state.

Create the durable conversation and upstream session on first send unless empty chats are explicitly useful. Disable Send while the first request is active to prevent duplicate threads.

## Pagination and search

Use server-side, scope-filtered search over both title and message text. Prefer a stable keyset cursor such as `(updated_at, id)` over offsets so new activity does not shift page boundaries.

For the client:

- Reset cursor, results, exhaustion state, and request generation when scope or query changes.
- Debounce search with native timers.
- Use `IntersectionObserver` for the sentinel.
- Deduplicate IDs when appending pages.
- Ignore stale responses with a generation counter or cancellation.
- Stop observing/fetching when no next cursor remains.

## Restore flow

Selecting a result should fetch durable conversation detail, render messages in ascending order, restore context metadata, set the active conversation, and continue through its existing upstream session. Do not silently replace a missing upstream session; expose a recoverable failure according to the host product’s contract.

## Legacy-data boundary

Older conversation rows may have session IDs but no local transcript. Give them an honest fallback title/date if useful, but do not claim historical body search or reconstruct content that was never stored.

## Verification recipe

Prove the complete lifecycle, not just list rendering:

1. Create thread A.
2. Start New chat and create thread B.
3. Confirm A and B have distinct local and upstream identities.
4. Reopen A and continue it.
5. Restart/reload and reopen A again.
6. Search by derived title.
7. Search by unique body text.
8. Load more than one page and verify no duplicates or skipped rows.
9. Change query/scope during an in-flight request and verify stale results never appear.
10. Exercise loading, empty, error, retry, keyboard, mobile, and console-error states.
