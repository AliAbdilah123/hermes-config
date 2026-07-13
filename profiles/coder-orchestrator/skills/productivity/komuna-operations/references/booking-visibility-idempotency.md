# Booking visibility and idempotency fixes

Use when Komuna users report booked sessions missing from **My bookings**, bookings rendering as `Unknown product`/`Unknown program`, cancel returning `not_found`, or session buttons remaining bookable after a booking.

## Durable debugging path

1. Reproduce from the API first, not only the UI:
   - `GET /api/v1/my/bookings` with the affected user header/session.
   - `GET /api/v1/programs/{program}/sessions?page=1&limit=...` with the same user.
   - Attempt duplicate `POST /api/v1/claims { sessionId }` only against a safe/test session or after confirming state can be restored.
2. Check whether `/my/bookings` selects joined columns but scans them with a base claim scanner. Symptom: JSON has empty `id`, empty dates, null session fields, and UI falls back to Unknown/TBD.
3. Check nullable SQL scans for claims: subscription-backed claims often have `voucher_id = NULL`; scanning nullable DB columns into plain strings can break cancel/detail responses.
4. Check duplicate active claims:
   ```sql
   SELECT pm.user_id, vc.session_id, COUNT(*) c, GROUP_CONCAT(vc.id)
   FROM voucher_claims vc
   JOIN program_members pm ON pm.id = vc.claimant_id
   WHERE vc.cancelled_at IS NULL AND vc.session_id IS NOT NULL
   GROUP BY pm.user_id, vc.session_id
   HAVING c > 1;
   ```

## Fix pattern

- Add a dedicated scanner/DTO for booking-list joined rows; include `product_id`, `product_name`, `program_id`, `program_name`, `session_start_time`, `session_end_time`, `session_capacity`, and `session_taken`.
- Do not ignore row scan errors in booking-list handlers; broken scans become misleading UI fallbacks.
- Add a server-side duplicate guard for active claims by the same user/session (`cancelled_at IS NULL`). Frontend disabling is not sufficient.
- Add a capacity guard before creating a claim; ensure `sessions.taken` is not incremented for duplicate or failed inserts.
- For claim detail/cancel helpers, scan nullable columns with `sql.NullString` and emit JSON nulls.
- Extend session-card list endpoints with `bookedByCurrentUser` computed from the current user + active claims, so the UI can render a disabled `Booked` state.
- Standardize member-facing session action copy to `Book`/`Booked`; avoid mixed `Reserve` labels unless product requirements explicitly distinguish reservation vs booking.
- If an unrelated bookings sub-tab is non-functional (for example a compensation `Vouchers` tab inside My Bookings), remove it unless the product requirement is explicit.

## Verification checklist

- Backend: add/keep tests for populated `/my/bookings`, cancelling nullable subscription claims, and duplicate booking returning conflict.
- Frontend: typecheck/build and update tests that assert booking/reserve copy.
- Live smoke checks:
  - `/my/bookings` returns a real claim id and populated product/program names.
  - `/programs/{program}/sessions?...` returns `bookedByCurrentUser: true` for already-booked sessions.
  - duplicate `POST /claims` returns `409 already_booked`.
- If previous duplicate rows polluted live data, clean duplicates by keeping the newest active claim per user/session and decrementing `sessions.taken` by the number cancelled; do this inside a transaction and verify no duplicate groups remain.
