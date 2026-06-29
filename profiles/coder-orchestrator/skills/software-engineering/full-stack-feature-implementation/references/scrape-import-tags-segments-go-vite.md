# Scrape import → potential tags → segments in local Go + SQLite + Vite apps

Use this when implementing a scraped local-business dataset workflow in the user's local Go + SQLite + React/Vite apps.

## Durable pattern

1. **Start with a kanban/todo board** for plan-driven implementation. Keep final integration, build, deployment, and public verification in the parent session.
2. **Preserve existing in-progress work**. Check git status/diff first; if the working tree already has unrelated edits, layer changes carefully rather than resetting or overwriting.
3. **Implement scrape ingestion as schema detection, not a second endpoint**:
   - Accept existing app CSV headers and scrape headers in the same `/businesses/import` flow.
   - Detect scrape headers such as `Session ID`, `Title`, `Rating Score`, `Review Count`, `Coordinates`.
   - Normalize to the business model: name/title, phone, website URL, rating, review count, lat/lon, district, category, city, source session.
4. **Persist audit rows** in an `import_rows` table:
   - `tenant_id`, `import_id`, `row_number`, `raw_json`, `normalized_json`, `status`, `error`, optional `business_id`, `created_at`.
   - For rejected rows, store `business_id` as NULL rather than `0` when a foreign key exists.
5. **Count upserts correctly**. SQLite `ON CONFLICT DO UPDATE` can report affected rows for both inserts and updates; pre-check existence by tenant + natural key before calling the upsert if the response needs separate `inserted` vs `updated` counts.
6. **Treat coordinates as row-level validation**. Quoted CSV coordinates like `"-1.2654, 116.8312"` should parse; malformed non-empty coordinate strings should reject only that row and still complete the import with errors.
7. **Tags should remain explainable opportunity language**. Prefer tags like `No Website`, `Landing Page Offer`, `WhatsApp Ready`, `Catalog Opportunity`, `Review Trust`, `IKN Expansion`, `Commercial Interior`, `Needs Data Enrichment`; numeric scores are secondary.
8. **Segments are work queues**. Provide `/segments` summaries plus `/segments/:key/businesses` lists, and expose a bulk `add-segment-to-crm` action that is idempotent for active leads.
9. **Frontend should show operational feedback**:
   - Import summary with detected schema, inserted/updated/duplicate/error counts, and sample errors.
   - Business table columns for district/source, rating/reviews, tags.
   - Segment cards with counts, recommended action, “Open Segment”, and “Add CRM”.

## Verification checklist

- Backend tests cover scrape header mapping, coordinate parsing/rejection, import row audit persistence, tenant scoping, segment counts, and idempotent segment-to-CRM.
- Run `go test ./...` and `go build -o bin/<service> ./cmd/api`.
- Run the project frontend build script (`npm run build` for Vite apps).
- Deploy static assets and backend binary, restart the service, then verify:
  - local `/healthz`,
  - public app index and hashed JS asset,
  - deployed JS contains a feature marker such as `Segment Opportunity Engine`,
  - API smoke for `/segments` and a representative filtered `/businesses` query.

## Pitfalls

- Do not pass `0` into nullable foreign-key columns for failed import rows; SQLite will enforce FK references and silently lose audit rows if the insert error is ignored.
- Do not retry a failing full test command without inspecting the latest error; fix the test/data/code assumption first.
- For CSV tests with coordinates containing a comma, use quoted coordinates or raw string literals so the CSV reader sees one field.
- When service binary replacement fails with `Text file busy`, stop the systemd service, copy the binary, then start it again; verify readiness after a short moment rather than assuming immediate port availability.