# Multi-tenant timezone display pitfalls

Two recurring bug classes when displaying UTC-stored timestamps in a multi-tenant
app where each tenant has a configured timezone.

## Pitfall 1: Hardcoded timezone in display components

**Symptom:** Session times display correctly for one tenant but are off by 12+ hours
for others. The grouping into "Today/Tomorrow/Past" also appears inconsistent.

**Root cause:** A display component has a hardcoded timezone constant instead of
using the tenant/program's configured timezone from the API response.

**Example (Komuna):**
```typescript
// BROKEN — hardcoded, ignores program.timezone
const TZ = 'America/New_York'
formatTime(iso)  // always Eastern Time
```

**Fix pattern:**
1. Add `timezone` to the component's Props interface
2. Pass `program.timezone` (from the API response) down from the parent page
3. Use the prop in all `toLocaleTimeString`/`toLocaleDateString` calls

```typescript
// FIXED — accepts timezone as prop
function formatTime(iso: string, timezone: string): string {
  return new Date(iso).toLocaleTimeString('en-US', {
    hour: 'numeric', minute: '2-digit', hour12: true, timeZone: timezone,
  })
}
```

**Detection:** Search the codebase for `timeZone:` followed by a string literal.
All display-formatting timezone references should come from tenant/program data.

## Pitfall 2: Date-only day-grouping when sessions end same-day

**Symptom:** A session at 12:03 AM–1:03 AM today stays in the "Today" section
even at 3 PM (14 hours after it ended). It only moves to "Past" at midnight.

**Root cause:** The day-grouping function compares only date strings, not actual
timestamps. A session on today's date is always "Today" regardless of whether
its end time has passed.

**Example (Komuna):**
```typescript
// BROKEN — date-only comparison
function getDayGroup(startTime, timezone, now) {
  const sessionKey = formatDateKey(startTime, timezone) // "07/02/2026"
  const todayKey = formatDateKey(now, timezone)          // "07/02/2026"
  if (sessionKey === todayKey) return 'today'  // ← never checks time
  // ...
}
```

**Fix pattern:**
1. Add `endTime` parameter to the grouping function
2. When the session date matches today, also check if the end time has passed

```typescript
// FIXED — time-aware comparison
function getDayGroup(startTime, endTime, timezone, now) {
  const sessionKey = formatDateKey(startTime, timezone)
  const todayKey = formatDateKey(now, timezone)
  if (sessionKey === todayKey) {
    return new Date(endTime).getTime() < now.getTime() ? 'past' : 'today'
  }
  // ...
}
```

## Pitfall 3: Future dates falling through to "past"

**Symptom:** Sessions 2+ days in the future appear in the "Past" section.

**Root cause:** The day-grouping function's fallthrough `return 'past'` catches
ALL non-today/non-tomorrow dates, including future ones.

**Fix:** Use lexicographic date-string comparison to distinguish past from future:
```typescript
return sessionKey < todayKey ? 'past' : 'tomorrow'
// MM/DD/YYYY format sorts chronologically when zero-padded
```

## General debugging approach

1. **Trace the timezone flow:** DB (UTC) → API response (UTC ISO strings) → DTO
   (UTC strings) → Frontend display (should use `program.timezone`)
2. **Check for string literal timezones:** `rg "timeZone: ['\"]"` in the frontend
3. **Verify the display function signature:** Does it accept a `timezone` parameter?
4. **Check grouping logic:** Is it comparing full timestamps or just date strings?
5. **Test with a session that ended earlier today:** It should appear in "Past"
6. **Test with a session in a different timezone:** Times should reflect the
   program's timezone, not the developer's local timezone

## Reference: Komuna architecture specifics

- Timezone is stored per-program in the `programs.timezone` column (IANA string)
- Backend stores all timestamps in UTC
- Frontend receives UTC ISO strings like `"2026-07-02T17:03:00Z"`
- `formatSessionTimeRange()` in `all-sessions/format.ts` correctly uses
  `toLocaleTimeString(..., { timeZone: timezone })`
- Manager dashboard's `SessionCard.tsx` uses `formatTime(iso, timezone)` and
  `formatDateParts(iso, timezone)` — both need the program's timezone prop
- `getDayGroup()` in `ManagerDashboardPage.tsx` uses `formatDateKey()` with
  the program timezone to compute the calendar date in that timezone
