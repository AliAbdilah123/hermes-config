# Session template rollover + past history

Use this when fixing or reviewing Komuna admin session-template previews/history.

## Durable lesson

The admin Sessions tab's "next 5 sessions" must be computed from the product's configured session template (`weekly_slots`: `day_of_week`, `start_time`/`start_time_utc`, `duration_minutes`/`end_time`) and then filtered by the full occurrence end datetime, not by calendar date alone.

If today is an available day but the occurrence's `end_time` is already in the past, do not show it as activatable. Continue walking the weekly slots until the preview is filled back to 5 future occurrences.

## Implementation pattern

- Build preview occurrences from the product template/available-days only.
- Merge saved sessions by exact `start_time` so active/generated sessions replace previews.
- Treat sessions as future/upcoming only when `new Date(end_time) > now` and `lifecycle_status !== 'cancelled'`.
- Keep a UI guard in activation: if `end_time <= now`, show a message and do not call generate/activate.
- Add a read-only "Past activated" tab that queries the existing program sessions endpoint with a past filter (e.g. `/programs/:id/sessions?status=past&limit=50&sort=startTime_desc`) and does not render activation/deactivation controls.

## Verification

Add a focused frontend test for the rollover helper with an anchored `now`:

- Given weekly Monday/Tuesday/Wednesday/Sunday 17:00-18:00 slots.
- Given `now = 2026-07-13T18:01:00Z`.
- Assert Monday July 13 is absent and the list still contains 5 sessions, including the later fill-in occurrence.

Add a UI test for the history tab:

- Mock the past endpoint.
- Click the Past activated tab.
- Assert the past manager/booked count/product render.
- Assert Activate/Deactivate buttons are absent in the history view.

## Pitfalls

- Fake timers can hang `@testing-library/user-event`; prefer passing anchored `now` into pure helpers instead of globally freezing timers for interaction tests.
- Text like `3/10 booked` can be split across DOM text nodes. For tests, assert on `document.body.textContent` normalized whitespace or target a containing row.
