# Frontend Filter / API Query Triage

Use when a user reports that UI filter pills/tabs (for example `upcoming`, `ongoing`, `past`) visually switch but the result list does not change or always shows the default class of items.

## Root-cause pattern

The frontend can be correct while the active API ignores the query parameter. In Komuna-style SPA/API stacks, check both sides before editing UI layout:

1. Verify the frontend sends the selected filter in the API call.
   - Inspect URL/query-state helpers and API client calls.
   - Add/adjust a frontend test that clicks the filter and asserts the API call includes the new query value.
2. Probe the active deployed/local endpoint directly with each query value.
   - Example: `/programs/:id/sessions?status=upcoming|ongoing|past&page=1&limit=...`
   - Assert every returned item has the requested status, not just HTTP 200.
3. Inspect backend list handlers for ignored query parameters.
   - A common bug is building all rows, then returning them unchanged when `page` exists.
4. Inspect backend computed status logic.
   - For session-like time ranges, status must compare both start and end:
     - `now < start` => `upcoming`
     - `start <= now < end` => `ongoing`
     - `now >= end` => `past`
   - Checking only start time can never produce `ongoing`.
5. If public routes use slugs, ensure subresource handlers resolve slug to canonical ID before comparing foreign keys.
   - `/programs/:slug/sessions` should compare products/sessions against the program ID, not the slug string.
6. Keep layout changes out of filter bug fixes unless explicitly requested.
   - Fix returned data/status and dynamic headings; do not restyle the already-correct tab/page.

## Regression checks

- Backend test: seed one past, one ongoing, one upcoming row and assert each `status=` filter returns only matching rows.
- Frontend test: click Past/Ongoing and assert the API call uses the selected status and heading changes.
- Deployment verification: fetch the public endpoint for each status and print count plus distinct returned statuses.

## Pitfalls

- Empty `ongoing`/`past` results can be correct if seeded/demo data is all future; verify by checking returned statuses and data timestamps.
- Do not conclude the browser filter is broken until you have compared frontend API params with backend response behavior.
