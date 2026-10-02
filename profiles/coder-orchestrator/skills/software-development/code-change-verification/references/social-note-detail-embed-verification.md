# Social note-detail embed verification

Use when a messaging webhook stores a shared social post/Reel URL and note detail should render provider media rather than only a link.

## Contract sequence

1. Disambiguate the requested surface before editing: note detail, notes list, browser notification, and system notification are separate targets.
2. Treat the live callback shape as authoritative. Preserve provider-semantic type only when a stable discriminator was observed; do not infer `reel` merely because the sender says they shared a Reel.
3. Verify the persisted descriptor for the exact latest receipt (timestamp, hashed message ID, note ID, type, URL class). A successful `note_created` log does not prove the expected attachment type or URL was stored.
4. Build the official provider embed URL from the already allowlisted permalink using URL encoding. Keep the original external link as a visible, keyboard-accessible fallback.
5. Do not scrape provider HTML, proxy media bytes, guess CDN URLs, or replace a permalink with an unverified media URL.
6. Keep iframe titles semantic, lazy-load embeds, size responsively, and retain a focus-visible fallback target of at least 44px.

## Verification boundaries

- **Source/unit:** correct plugin selection, encoded permalink, iframe accessibility, and fallback link.
- **Deployment:** public note-detail lazy chunk contains the embed marker and the public HTML references the new build.
- **Authenticated browser:** open the exact owned note detail, prove the iframe is present with the expected provider plugin URL, inspect its rendered area, reload for persistence, test mobile width, and check console/network failures.
- Cross-origin iframe presence is not proof that provider media loaded. A provider may refuse private, deleted, login-gated, or non-embeddable content. Keep status as `implemented/deployed; authenticated visual E2E pending` until pixels or iframe load behavior are verified.

## Classification pitfall

A stored `fallback` descriptor may still point to a Reel and can often render through a generic post embed. Do not relabel it as a Reel unless the callback includes the observed Reel discriminator and persistence confirms the normalized `reel` type. Conversely, do not claim a Reel callback was verified merely because a later note has an HTTPS Facebook URL; correlate receipt time/message hash and stored note row.
