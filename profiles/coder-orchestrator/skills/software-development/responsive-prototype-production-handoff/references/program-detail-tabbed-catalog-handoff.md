# Tabbed catalog prototype → production handoff

Use this reference when an approved static program/catalog prototype becomes a real data-backed page.

## Production translation rules

- Treat the prototype as the visual contract, not the data source. Render only API records; never create a fake fourth item merely to demonstrate a four-column grid.
- Preserve existing auth, role guards, canonical slug routes, pricing/currency formatting, booking semantics, voucher FIFO rules, translations, themes, loading/error/empty states, and shared modal consumers.
- A tabbed page should expose one `tabpanel`, support ArrowLeft/ArrowRight/Home/End, honor hash deep links, and align the active tab inside a horizontally scrollable mobile strip without stealing focus.
- For initial/hash tab alignment, deterministic container `scrollLeft` is more reliable than smooth `scrollIntoView`; reserve animation for user-triggered motion. Include a jsdom-safe fallback when using browser scrolling APIs.
- Build carousels from already-fetched entities. Keep missing-media entries and use typed placeholders rather than dropping records. On mobile, reserve separate geometry for stage, caption, and counter/dots so text layers cannot overlap.
- Avoid duplicate placeholder and caption titles on small screens; show one title treatment and retain the placeholder type label.
- Mobile rows with variable-length titles need a fixed or tightly bounded anatomy. Clamp/ellipsis the title so it cannot increase row height; preserve time, status, and a >=40px action.
- For dense two-column mobile catalog cards, constrain total height explicitly, clamp secondary descriptions first, and never hide price or purchase affordance.

## Verification sequence

1. Add focused tests for semantics and responsive CSS contracts before implementation.
2. Run changed-file lint, feature/regression tests, and production build independently.
3. Run repository-wide lint/tests separately; report unrelated baseline failures without editing unrelated code.
4. Verify the real API endpoint and the frontend proxy independently before judging a loading/error screenshot.
5. Exercise the generated production bundle with `vite preview` (or the project equivalent), not only a long-running HMR server. Production preview is the authoritative visual artifact when dev-only HMR behavior is suspect.
6. Capture desktop Overview/Sessions/Products/Packages and mobile equivalents, including modal states and light/dark themes.
7. Inspect console errors, network failures, page-level overflow, active-tab visibility, missing-image fallbacks, actual data counts, and route targets.
8. Deploy the fresh build, verify public HTTP status plus served asset hashes, then commit/push only task-related files.

## QA interpretation pitfalls

- A partially visible *inactive* tab may be a deliberate scroll affordance; the selected tab itself must be brought fully into view.
- Card width and card height are separate acceptance criteria. Measure the requested dimension rather than inferring it from a screenshot.
- Do not accept a screenshot of an error/loading state as visual evidence. Diagnose API/proxy readiness and recapture after data settles.
- If a visual QA tool flags intentional ellipsis as clipping, distinguish secondary-copy truncation from hidden essential content.
