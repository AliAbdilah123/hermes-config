# Komuna data-backed Discovery merchandising landing

Use this when implementing an approved Komuna landing/Discovery prototype with ranked program sections and a real-image carousel.

## Selection model

- Fetch one sufficiently large, consistent `/programs` result set.
- Restrict merchandising candidates to real joinable visibility states (`public`, `need_approval`) unless product policy explicitly says otherwise.
- Select sections in reservation order:
  1. Most Popular: member count descending, rating descending, stable name tie-break.
  2. New Programs: exclude Popular, then real `created_at` descending.
  3. Open to Join: exclude both prior sets, Fisher–Yates shuffle once per page load, then take the display limit.
- Never backfill short sections with duplicates.
- Keep Open stable across rerenders, locale/theme changes, carousel ticks, and membership refreshes. Retry/remount may resample.
- On a refresh that can change Popular/New rankings, preserve prior Open IDs only after removing IDs now reserved by Popular/New. Add a regression test for this ranking-change case.

## API timestamp integrity

Do not trust a DTO field merely because the database query scans it. Trace the value end-to-end: schema → query scan → model field → DTO serializer → public JSON. In Komuna's local Go API, `programs.created_at` was scanned into a local variable but discarded while `programDTO` returned a constant. The minimal correction was to add `Program.CreatedAt`, assign the scanned value in list/detail paths, and serialize it. No schema migration was needed because the column already existed.

## Carousel integration

- Reuse `publicAssetUrl()` for API-provided relative image paths.
- Broken images must render the established decorative/placeholder fallback, not become a hidden blank area.
- Use slug-first, ID-fallback program links.
- Four-second autoplay; pause on pointer hover and keyboard focus; clean up timers; suppress autoplay under reduced motion; avoid autoplay for one slide.
- Test asset URL resolution, broken-image fallback, ID route fallback, focus pause, timer cleanup, and reduced motion.

## Verification and delivery

1. Run focused selector, carousel, and Discovery page tests.
2. Run `api/v1` Go tests when DTO wiring changes (the Go module may live there rather than the parent `api/` directory).
3. Build Vite with `VITE_NEON_AUTH_URL` removed from the build environment.
4. Deploy frontend from the generated `dist/` to the nginx root actually serving Komuna; deploy/restart the API only if API code changed.
5. Verify public index asset hashes and both JS/CSS return 2xx.
6. Verify public `/api/v1/programs` returns a real, non-constant `created_at`.
7. Commit and push only after live verification succeeds.

## Pitfalls

- A callback depending on i18next's `t` can recreate an effect and silently refetch/reshuffle on language changes. Keep network callbacks locale-independent; translate error keys at render time.
- Preserving Open IDs without subtracting newly ranked Popular/New IDs breaks the mutual-exclusion invariant after membership/rating changes.
- A synchronous route assertion for section content will fail because Discovery fetches asynchronously; await the heading.
- Treat prototype visuals as composition guidance while retaining shared `TopNav`, `Footer`, `ProgramGrid`, `ProgramCard`, auth, theme, i18n, and route behavior.
