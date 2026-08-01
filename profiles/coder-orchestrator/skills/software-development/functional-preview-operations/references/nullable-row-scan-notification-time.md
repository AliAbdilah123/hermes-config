# Nullable SQL row scans and notification-time preview proof

When an unread/new notification renders `Invalid Date` despite a valid database timestamp, inspect the entire SQL scan sequence before changing frontend formatting.

## Failure mechanism

Go scanning a SQL `NULL` into a plain `string` fails. If the `rows.Scan(...)` error is ignored, later destinations remain zero values, so a valid database `created_at` can become `created_at: ""` in the API. Unread notifications often combine nullable `program_id` and nullable `read_at`; fixing only one leaves the same cascade at the next nullable field.

## Minimal diagnosis and fix

1. Confirm the stored timestamp is valid.
2. Inspect every selected column before it for nullable schema/data.
3. Check `rows.Scan` errors explicitly.
4. Reproduce the exact state combination, such as `program_id IS NULL` plus `read_at IS NULL`.
5. Use `COALESCE(column, '')` when the internal model intentionally uses strings and DTO conversion maps empty back to JSON null, or use `sql.NullString` when nullness must remain explicit.

## Regression and public E2E

- Seed an unread row with every implicated nullable field set to `NULL` and a known timestamp.
- Assert the public authenticated API returns `read_at: null` and non-empty `created_at`.
- Render the exact notification page and assert the `<time>` value is human-readable and the page has no `Invalid Date`.
- Keep fixture title/body neutral: do not include the forbidden phrase itself in explanatory copy, or whole-page negative assertions produce a false failure.
- Verify production with a disposable identity/notification in the real production DB only when authorized, then delete the notification, sessions, auth identity, and user records after browser proof.
