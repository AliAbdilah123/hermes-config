# Calendar day post list pattern

Use when users say the month calendar is hard to review because many posts share the same day.

## Durable implementation pattern

- Keep the existing month fetch (`/api/calendar/posts?month=YYYY-MM`) as the data source; do not add a backend endpoint unless the month payload becomes too large.
- Add a pure helper that filters posts by the user's local calendar day and sorts by `publishAt`:
  - Convert both the selected `Date` and each `post.publishAt` with `toZonedTime(..., userTimezone)`.
  - Compare `format(..., "yyyy-MM-dd")`.
  - Sort ascending by ISO `publishAt`.
- Add a small Vitest test for timezone-boundary behavior before implementing UI.
- In the grid, avoid making the entire droppable cell clickable because it can interfere with drag/drop. Use a deliberate date-number button and/or `View all (N)` affordance.
- Preserve existing `useDroppable` day cells and `useDraggable` post cards; only add `onDayClick` plumbing.
- Render a separate responsive dialog for the day list. Keep the body scrollable (`max-height` around `min(70vh, 620px)`) while the calendar behind remains stable.
- Clicking a row should close the day-list dialog and open the existing post detail modal, rather than stacking two dialogs.

## Verification

```bash
cd /home/ubuntu/socialzen/apps/frontend
pnpm test src/lib/calendar-day.test.ts
pnpm typecheck
pnpm build
sudo rsync -a --delete dist/ /var/www/html/projects/socialzen/
sudo chown -R www-data:www-data /var/www/html/projects/socialzen
curl -sI http://localhost/projects/socialzen/ | head -1
JS=$(basename $(ls /var/www/html/projects/socialzen/assets/CalendarPage-*.js | head -1))
curl -sI "https://socialzen.ahsanworks.com/projects/socialzen/assets/$JS" | grep -i content-type
curl -s "https://socialzen.ahsanworks.com/projects/socialzen/assets/$JS" | grep -o "View all" | head -1
```

Expected: tests/typecheck/build pass, production CalendarPage chunk is `application/javascript`, and the chunk contains the visible `View all` marker.
