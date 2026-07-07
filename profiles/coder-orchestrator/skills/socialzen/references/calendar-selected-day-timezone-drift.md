# Calendar selected-day timezone drift

Use when the month calendar visibly shows posts on a date, but clicking the date/post opens the day-list dialog with `0 posts` / `No posts on this day`.

## Symptom

- Grid day cells show scheduled/published post cards or `View all (N)`.
- Clicking the date number, `View all`, or a post opens the day dialog.
- Dialog title is the clicked date, but the list is empty.
- Public/deployed JS contains the day-list dialog markers, so this is not necessarily a stale deploy.

## Root cause pattern

The grid and dialog compute the selected date key differently.

Common bad shape:

```ts
// grid
const key = format(day, "yyyy-MM-dd")
const postsByDay = postsByLocalDay(posts, userTimezone)

// dialog helper
const dayKey = format(toZonedTime(day, userTimezone), "yyyy-MM-dd")
```

`day` is already the calendar cell `Date`. Re-zoning that selected cell date can shift the key when browser/system timezone differs from the profile timezone, so the grid can show posts under one key while the dialog looks up another key.

## Fix

Use one shared keying rule for both grid display and selected-day lookup.

Smallest safe fix:

```ts
export function postsForLocalDay(posts: CalendarPost[], day: Date, userTimezone: string): CalendarPost[] {
  const dayKey = format(day, "yyyy-MM-dd")
  return postsByLocalDay(posts, userTimezone).get(dayKey) ?? []
}
```

If the grid later changes to compute cell keys in the user timezone too, extract a shared `localDayKey(date, userTimezone)` helper and use it in both places. Do not let grid and dialog each invent their own date key.

## Regression test shape

Add/keep a Vitest test where the selected day `Date` and user timezone could otherwise shift across midnight. Assert the helper returns exactly the posts visible for the clicked grid key, sorted by `publishAt`.

## Verification

```bash
cd /home/ubuntu/socialzen/apps/frontend
pnpm test src/lib/calendar-day.test.ts
pnpm typecheck
pnpm build
```

After deploy, verify the public CalendarPage chunk is JavaScript and contains dialog markers (`Posts on`, `No posts on this day`, `View all`) before blaming CDN/cache.
