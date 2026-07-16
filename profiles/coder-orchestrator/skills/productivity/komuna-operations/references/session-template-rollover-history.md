# Session template rollover + activated history

Use this when fixing or reviewing Komuna admin session previews and the read-only **Past Activated** history.

## Behavioral contract

- Build each product’s “next 5 sessions” from its configured weekly slots.
- Exclude an occurrence once its **end wall-clock time** has passed in the program timezone, then keep walking the schedule until five future occurrences are available.
- **Activated + ended** sessions belong in **Past Activated**.
- **Inactive + ended** sessions disappear from Upcoming but never enter activation history.
- Past Activated is read-only and newest-first.

## Time representation: pseudo-UTC wall clocks

Komuna session/template timestamps may carry a trailing `Z` while representing the program’s local wall clock rather than a true UTC instant. Do not compare those values directly with `time.Now()` or `new Date(...)` unless the storage contract has first been confirmed.

For the current contract:

- Load the program timezone, falling back safely to UTC.
- Parse stored session wall clocks in that location (Go: `time.ParseInLocation` with the stored layout).
- Compare against the real current instant.
- In frontend preview generation, convert `now` to a program-local wall-clock key and compare like with like.
- Test both a positive offset such as `Asia/Makassar` and a negative offset; date-boundary bugs often pass one side and fail the other.

## API history contract

The frontend requests history like:

`/programs/:id/sessions?status=past&limit=50&sort=startTime_desc`

The request may omit `page`. Therefore:

- Any filtered sessions response must return the paginated envelope expected by the frontend (`items`, `page`, `limit`, `total`, `hasMore`), not switch shape based only on the presence of `page`.
- Apply the past classification using the program timezone.
- Restrict Past Activated to persisted sessions with `is_active = 1`; an ended inactive preview is not history.
- Keep product/program scoping in the database query.

## Implementation pattern

- Build preview occurrences from product templates/available days.
- Merge persisted sessions by exact start time so generated/activated records replace previews.
- Filter cancelled sessions independently of temporal classification.
- Keep an activation guard: if the occurrence has ended in program-local time, do not call generate/activate.
- Reuse the existing status-filtered endpoint and read-only history view; avoid adding a new data layer.

## Regression tests

1. **Preview rollover:** anchor `now` after a local morning slot ends; assert that slot is absent and the list still contains five later occurrences.
2. **Offset symmetry:** add a negative-offset case where a later same-day slot remains upcoming.
3. **Status classification:** given a stored `09:00–10:00` wall clock and `now` after 10:00 in `Asia/Makassar`, assert status is `past`.
4. **History endpoint:** insert one ended active and one ended inactive session; call the exact frontend URL without `page`; assert the response envelope contains only the active session.
5. Check fixture insert errors explicitly. Include all required schema columns and reference a seeded active product, otherwise an ignored SQL error or inner join can produce a misleading empty result.

## Verification

- Focused Sessions frontend tests.
- Changed-file ESLint and frontend production build.
- Full Go tests and Go build.
- Independent review focused on timezone semantics and endpoint response shape.
- Rebuild the API binary at the path used by its systemd unit, restart via `sudo -n systemctl restart ...`, inspect service status/logs, and probe the configured listen port rather than assuming a port.
- Verify Git local/remote SHA equality and public site HTTP status.

## Pitfalls

- Fake timers can hang `@testing-library/user-event`; inject anchored `now` into pure helpers instead.
- A green unit test for the classifier does not prove the frontend endpoint works; test the exact query and JSON shape.
- Do not silently discard fixture setup errors (`_, _ = db.Exec(...)`). Fail immediately so schema and foreign-key/join mistakes are visible.
- A service may restart successfully on a different port than an old smoke-test command assumes; inspect the unit/status before declaring deployment unhealthy.
- Text such as `3/10 booked` may span DOM nodes; assert normalized container text or target the containing row.
