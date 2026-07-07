# Calendar crowded-day post list UX

When the user reports that the calendar month view is hard to scan because many posts land on the same date, treat it as a frontend calendar UX issue before considering API/schema changes.

## Existing SocialZen calendar shape

- Page: `apps/frontend/src/pages/calendar/CalendarPage.tsx`
- Grid: `apps/frontend/src/pages/calendar/CalendarGrid.tsx`
- Data/API type: `apps/frontend/src/lib/calendar.ts`
- Existing detail modal: `apps/frontend/src/pages/calendar/PostDetailModal.tsx`
- `CalendarGrid.tsx` already groups the loaded monthly `posts` array by local date using `toZonedTime(post.publishAt, userTimezone)` and `format(..., "yyyy-MM-dd")`.
- Day cells are already `useDroppable` targets and post cards are `useDraggable`; do not break drag/drop rescheduling.

## Smallest good approach

1. Keep the existing month fetch and derive the selected date's post list client-side from the already-loaded monthly posts.
2. Add `selectedDay: Date | null` in `CalendarPage.tsx` and compute `selectedDayPosts` by local-day key in `userTimezone`.
3. Pass `onDayClick` into `CalendarGrid.tsx`.
4. Make a deliberate click target in each cell (date number or `View all (N)`), not the entire droppable cell, to avoid conflict with dragging.
5. Add a focused `DayPostListDialog.tsx` that shows a scrollable list for the selected date and forwards row clicks to the existing `PostDetailModal`.

## UX notes

- Use a reference-card style: header with date/count, rows with thumbnail/account/caption, post type badge, status pill, and localized time.
- Body scrolls with a generous max height such as `min(76vh, 760px)`; the page behind should not scroll just to inspect a busy day, and dates with more than 3 posts must reveal the rest by scrolling inside the popup.
- Make the dialog visibly wider than the default shadcn dialog (`w-[min(94vw,980px)] max-w-none` worked well) so the row cards don't feel cramped.
- User-facing calendar post clicks should open the selected-day list first, not the post detail directly; keep detail access from a row inside the list.
- Preserve account filters by deriving the dialog list from the already-filtered `posts` state.
- Include all statuses unless the user asks to narrow to scheduled posts.
- Use SocialZen theme variables (`var(--card)`, `var(--line)`, `var(--ink)`, `var(--ink-3)`) to avoid dark-mode regressions.

## Verification

- `pnpm typecheck`
- `pnpm build`
- Manual check: busy date opens a scrollable list; post row opens detail modal; drag/drop still reschedules scheduled posts; account filter affects both grid and dialog; no horizontal overflow on mobile.
