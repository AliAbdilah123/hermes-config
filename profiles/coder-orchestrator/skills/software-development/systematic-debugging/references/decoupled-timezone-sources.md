# Decoupled Timezone Sources in Multi-TZ Web Apps

## Pattern

When a user reports that session/event times on a page don't match expectations — times look wrong, or items that should be "past" are still in "upcoming" sections — the root cause is often **two different timezone sources** in the same feature:

1. **Display layer**: `formatTime()` / `toLocaleTimeString()` — what the user SEES
2. **Categorization/Logic layer**: `getDayGroup()` / `isPast()` / `isToday()` — what determines which section the item goes in

If these use different timezone values, the UI becomes internally inconsistent: the displayed time says one thing, the section placement says another.

## Detection

Grep for `timeZone:` or `timezone:` in the display component. If it's a **hardcoded literal** (e.g., `'America/New_York'`) while other parts of the page use a **program-configured/prop-passed timezone**, the two layers are decoupled.

```bash
# Quick smoke test — find hardcoded timezone in display components
rg "timeZone:\s*'[^']+'" --type tsx
rg "timezone:\s*'[^']+'" --type tsx
```

## Fix

1. Remove the hardcoded TZ constant from the display component
2. Make `formatTime()` / `formatDateParts()` accept `timezone` as a parameter
3. Pass the program/tenant timezone as a prop from the parent page
4. Verify the same timezone value reaches both display and logic layers

## Variant: Date-only vs Time-aware comparison

Even with correct timezone, if the categorization layer only compares **dates** (e.g., `formatDateKey(start) === formatDateKey(now)`) without checking actual times, sessions that ended earlier today still show as "today" instead of "past."

Check: does the comparison use `endTime < now` or just `date(startTime) === date(now)`?

## Variant: Fallthrough mislabeling

Date-grouping functions that only handle `today` and `tomorrow` with a `return 'past'` fallthrough will mislabel future sessions (3+ days out) as "past." Fix with lexicographic date-key comparison:

```typescript
return sessionKey < todayKey ? 'past' : 'tomorrow'
```

(Works because `MM/DD/YYYY` zero-padded format sorts chronologically.)

## Example (Komuna Manager Dashboard)

- **Display**: `SessionCard.tsx` had `const TZ = 'America/New_York'` — hardcoded
- **Logic**: `getDayGroup()` used `program.timezone` from API — dynamic
- **Symptom**: Sessions in Asia/Jakarta showed times in Eastern US, and past/upcoming categorization didn't match the displayed times
- **Fix**: Removed hardcoded TZ, passed `timezone` as prop from parent, unified both layers to use `program.timezone`
