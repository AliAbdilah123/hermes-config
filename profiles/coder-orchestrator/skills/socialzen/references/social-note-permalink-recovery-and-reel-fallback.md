# Social-note permalink recovery and Reel fallback

Use this pattern when social-note webhook payloads contain stable media IDs/direct media but omit a canonical Instagram permalink.

## Contract

- Keep webhook ingestion network-free. Persist the provider-supplied media ID, direct media URL, external message ID, and any permalink already present.
- Recover missing permalinks lazily from an authenticated note-detail media-resolution request, using the stored external message ID.
- Validate recovered values through the existing canonical Instagram permalink parser; never persist arbitrary provider response strings.
- Persist only successful recovery so future detail loads do not repeat provider lookup. Leave missing values unchanged on lookup failure so a later detail load can retry.
- Return refreshed attachment metadata together with resolved/cached media. The detail client must replace its stale attachment data with that response, otherwise the newly recovered link exists only in storage and is not visible until reload.
- Preserve note ownership and CSRF checks on the resolver. Scope attachment updates by both note ID and user ID.

## Reel rendering fallback

- Prefer cached native video when available.
- If the attachment is a Reel, has a validated permalink, and has no cached playable video, render Instagram's official `/<reel-path>/embed/` iframe.
- Keep an external `Open on Instagram` link even when the embed is shown; embeds can be blocked by privacy settings or provider policy.
- Give the iframe a descriptive title, lazy loading, explicit media permissions, and a stable responsive size.
- Do not render both native cached video and the embed for the same attachment.

## Strict TDD sequence

1. Backend RED: create a note with a media attachment lacking `permalink` but having an external message ID. Stub one message lookup returning a canonical post/Reel URL. Assert the resolver persists the permalink and a second resolver call performs no lookup.
2. Frontend RED: assert the Reel embed is gated by `reel && permalink && !cachedPlayableVideo`, has a title, and retains the external-link fallback.
3. GREEN with the smallest store update, resolver response extension, and renderer condition.
4. Run focused tests, then complete backend tests, frontend tests/typecheck/build, and deployment smoke checks.

## Deployment verification pitfall

Do not assume a familiar local API port or health path. Read the actual service unit/log startup line, then probe its bound address and public reverse-proxy health route. A successful restart plus a 404 from a guessed port is not an application failure; verify the real listener before diagnosing the release.
