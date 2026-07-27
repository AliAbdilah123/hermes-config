# Application-wide date formatting safety

Use when any SocialZen page throws `RangeError: Invalid time value`, or when auditing date rendering against sparse historical/provider data.

## Root cause pattern

Frontend DTO types do not validate runtime values. Nullable database columns and SQL fallbacks such as `COALESCE(timestamp, '')` can produce `null`, `undefined`, or empty strings; provider and historical rows can also contain malformed text. Passing any resulting invalid `Date` to date-fns `format()`, `Intl.DateTimeFormat.format()`, or formatting logic that assumes valid date parts can throw during React render and crash a route.

## Shared boundary

Keep one small shared formatter, for example:

```ts
import { format, isValid } from "date-fns"

export function safeFormatDate(
  value: string | Date | null | undefined,
  formatString: string,
  fallback = "—",
): string {
  if (value == null || value === "") return fallback
  const date = value instanceof Date ? value : new Date(value)
  return isValid(date) ? format(date, formatString) : fallback
}
```

Use a context-appropriate fallback (`—`, `Unknown`, `Never`, or `Posted date unavailable`). Never invent a timestamp.

## Audit scope

1. Search all frontend `*.ts` and `*.tsx` files for date-fns `format`, native `toLocaleDateString`/date `toLocaleString`, `Intl.DateTimeFormat(...).format`/`formatToParts`, and helpers that manually read `Date` fields.
2. Classify each input:
   - API, database, provider, user, or persisted input: validate before formatting.
   - Locally constructed invariant such as `new Date()` or controlled calendar state: direct formatting is acceptable when its validity is established by construction.
   - Number/currency `toLocaleString`: not a date call; leave it alone.
3. Replace unsafe display formatting with the shared helper.
4. For non-display calculations (analytics grouping, best posting time, notification age, calendar grouping), validate first and skip or safely bucket invalid records rather than converting a fallback label into business data.
5. Guard editor hydration helpers too: an invalid scheduled timestamp should produce an empty field rather than `NaN-NaN-NaNTNaN:NaN`.
6. Audit backend date origins. Prefer nullable JSON for absent timestamps, but preserve historical compatibility; frontend rendering must remain safe even if old rows contain empty or invalid values.

## TDD and verification

1. Add utility regression cases for `null`, `undefined`, `""`, malformed text, valid ISO text, and a valid `Date`.
2. Add focused behavior coverage where invalid dates affect calculations, not only labels (for example Analytics best-time aggregation must ignore invalid timestamps).
3. Confirm RED before adding the utility/guards.
4. Run focused date/Analytics tests, the full frontend suite, typecheck, configured lint, and production build independently. A known unrelated full-suite failure must not suppress typecheck/build evidence; report each gate separately.
5. After deployment, verify the exact current Analytics chunk referenced by the current public index, with `Content-Type: application/javascript`; an old hashed chunk containing the guard is not proof.
6. Commit every newly created utility/test file explicitly. Before reporting completion, check for untracked frontend files after the first commit; `git diff --name-only` omits untracked files and can accidentally leave the shared utility out of the pushed commit even though the local build succeeded.

## Pitfalls

- A truthiness check only handles empty/null values, not malformed non-empty strings.
- `new Date(value)` does not validate; call date-fns `isValid()` before formatting.
- `Intl.DateTimeFormat` can throw on invalid dates too.
- Do not blanket-replace known-valid calendar `Date` formatting or numeric `toLocaleString`; audit by data boundary, not by method name alone.
- A local production build can import an untracked utility successfully. Verify the utility and its tests are tracked and pushed before deployment claims.
