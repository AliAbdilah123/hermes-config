# Manager Dashboard Implementation (Go API)

The manager dashboard at `GET /api/v1/programs/:id/manage/products/:pid/dashboard`
was originally a **stub** returning hardcoded empty data. This reference documents
the real implementation so future work doesn't need to rediscover the data model.

## Route Handler

The `manager()` function at ~line 1140 of `main.go` handles:
- `GET .../dashboard` → `buildManagerDashboard()`
- `GET .../session-claims` → `query voucher_claims` for the product

## Data Flow

```
programTree() → manager() → buildManagerDashboard(programID, productID)
                                  │
                                  ├─ Query program.timezone
                                  ├─ Compute todayStart/todayEnd in program's loc
                                  ├─ SELECT sessions WHERE start_time BETWEEN today
                                  ├─ SELECT COUNT(*) FROM requests WHERE pending
                                  ├─ countAttendance(todaySessionIDs)
                                  ├─ SELECT sessions for 7-day range
                                  └─ countAttendance(sevenDaySessionIDs)
```

## Timezone Handling

- Store UTC in DB (`start_time TEXT` in ISO 8601)
- Load program's timezone from `programs.timezone` column
- Use `time.LoadLocation(tz)` and `time.Date()` in that location to compute midnight
- Query DB using UTC-formatted strings: `todayStart.Format("2006-01-02T15:04:05Z")`
- This ensures "today" is computed in the program's timezone, not UTC

## Response Shape

```json
{
  "todays_sessions": [
    {
      "id": "ses-...",
      "title": "Morning Boxing",
      "start_time": "2026-07-02T22:00:00Z",
      "end_time": "2026-07-02T23:00:00Z",
      "coach": "Coach Ali",
      "is_active": true,
      "capacity": 15,
      "taken": 0,
      "status": "scheduled"
    }
  ],
  "activation_status": {
    "is_active": true,
    "has_sessions_today": true
  },
  "pending_approvals_count": 0,
  "attendance_summary": {"present": 0, "absent": 0, "unmarked": 2},
  "attendance_summary_7d": {"present": 5, "absent": 1, "unmarked": 8}
}
```

**Field naming convention:** The Go API uses snake_case JSON keys (`todays_sessions`, `start_time`, `is_active`, `attendance_summary_7d`). This is different from the Worker API which has a DTO layer that maps camelCase service types to snake_case HTTP responses. When adding new fields to the Go API, use snake_case directly.

## `countAttendance()` Helper

Takes `[]string` session IDs, queries `voucher_claims` table:
- `present`: `attendance_status='present'`
- `absent`: `attendance_status='absent'`
- `unmarked`: `attendance_status IS NULL OR attendance_status='pending'`

Uses `IN (?,?,...)` with dynamic placeholders (Go's `database/sql` doesn't support array binding).

## Frontend Consumption

The frontend `ManagerDashboardPage.tsx` expects `ManagerDashboardDTO` (defined in `apps/web/src/lib/api-types.ts`). The Go API's snake_case keys are automatically mapped by the `ApiClient`'s JSON parsing (no transformation layer). Fields added to the Go API response are immediately available in the frontend's `data` object.

## Key Pitfalls

1. **Don't overwrite `pendingCount`** — the variable is used for both `requests.status='pending'` count and the final response. Use separate variables for intermediate queries.
2. **`defer rows.Close()`** — always call after `rows != nil` check, before the `for rows.Next()` loop. Go defers execute at function exit (not block exit), so one `defer` per rows variable is sufficient.
3. **SQLite date comparisons** — store as ISO 8601 strings, compare lexicographically. The Go API formats as `"2006-01-02T15:04:05Z"` (Go's reference time).
4. **The Node.js Worker API (`apps/api/src/`) is NOT the production backend** — don't implement features there expecting them to go live. The Go API at `api/v1/main.go` serves real traffic on port 8095.
