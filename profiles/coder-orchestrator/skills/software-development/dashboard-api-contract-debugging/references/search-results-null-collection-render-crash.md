# Search results: fast API, permanent loader

Use when search appears slow or missing although the API returns `200` with the expected record.

## Diagnostic split

1. Measure the real dataset and inspect the SQL plan before adding FTS/indexes. A tiny per-user dataset makes database scale an unlikely cause.
2. Capture the search response body, browser `pageerror`/console, current URL, and visible body text together.
3. If the payload contains the expected row but the UI remains on loading, inspect every nested collection used by `.length`, `.map`, or `.join`.

Go nil slices encode as JSON `null`. This can affect nested fields such as `sections[].heading_path`, not only top-level result arrays. A frontend expression like `section.heading_path.length` then throws after the successful response, leaving the loader visible and making correct search look slow.

## Minimal durable fix

- Server: initialize collection fields to non-nil empty slices so JSON uses `[]`.
- Client: tolerate `null` during mixed-version deployment (`value?.length`, `(value ?? []).map(...)`).
- Requests: if scope changes should apply immediately, make the scope control issue a new search request; do not require another Search click.
- Races: cancel old requests or use a monotonically increasing request ID so an older response cannot replace newer scope/query results or clear their loading state.

## Verification

- RED regression proves the nested collection is non-nil in serialized/search output.
- Focused frontend regression covers immediate scope re-request and stale-response suppression.
- Authenticated public browser flow creates a uniquely identified note, searches by body content, changes scope to Content, and verifies the visible result plus `search_in=content` request.
- Require no page errors/console errors, clean fixtures, and database integrity afterward.

Do not call attachment-only notes searchable by content when their stored textual content is empty; attachment metadata/captions require a separate explicit search contract.
