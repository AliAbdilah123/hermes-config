# Calendar drag-and-drop rescheduling

Use this when extending the existing month-calendar drag/drop behavior in `apps/frontend/src/pages/calendar/CalendarPage.tsx` and `CalendarGrid.tsx`.

## Existing flow

- Reuse `@dnd-kit/core`; `DndContext` owns `handleDragEnd`, cards use `useDraggable`, and day cells use `useDroppable` with `data: { date }`.
- Monthly posts are held in component state and a keyed cache; persistence uses the existing `reschedulePost()` PATCH helper.
- The current handler combines the dropped year/month/day with the post's prior clock time and immediately updates state/cache before PATCHing.

## Safe UX extension

1. Do no validation, cache mutation, or API work during pointer movement. Handle it after drag end so dragging stays smooth.
2. Convert using the configured profile timezone, not the browser timezone. Treat calendar-cell dates as local day identities and post timestamps as UTC ISO values.
3. Stage a valid drop instead of PATCHing immediately. Open a compact confirmation dialog prefilled with the dropped date and the post's existing exact local time.
4. Let users edit both date and time. Validate the staged timestamp against a fresh `Date.now()` on initial drop and again on Save.
5. If the result is at or before now, leave post state/cache untouched and show an accessible inline message such as `Choose a future date and time.`
6. Cancel must preserve the original schedule. Save performs the single optimistic state/cache update and PATCH.
7. On PATCH failure, invalidate the relevant month/account cache, reload it, and surface a visible error.

## TDD checks

Add focused tests around a small pure helper before UI code:

- preserves the exact local publish time, including seconds/milliseconds, when changing only the day;
- rejects a resulting timestamp at or before a fresh `now` value;
- rejects nonexistent local wall-clock times by round-tripping the UTC conversion back through the profile timezone (DST gaps must not silently normalize);
- converts edited date/time to the correct UTC ISO in the user's timezone;
- handles dates where browser and profile timezones differ.

Add a focused page-level test with the DnD grid mocked at the event boundary. Assert:

- an invalid drop shows an accessible `role="alert"`, opens no dialog, and makes no persistence call;
- a valid drop opens the dialog but makes no persistence call;
- Cancel closes the dialog without persistence;
- Save performs exactly one persistence call with the edited timestamp;
- a rejected PATCH reloads the month and shows a visible error after the optimistic update.

Then run the focused Vitest targets, typecheck, and production build. Confirm no PATCH occurs merely because a drag ended; persistence starts only after Save. After deployment, grep the generated `CalendarPage-*.js` for the validation copy and verify the public asset returns `content-type: application/javascript` before reporting success.

## Scope ceiling

No backend/schema change and no new DnD/date dependency are needed. Reuse the existing dialog, input, button, cache, and PATCH paths.
