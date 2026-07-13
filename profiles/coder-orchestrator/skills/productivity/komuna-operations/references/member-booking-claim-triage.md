# Komuna member booking / claim triage

Use when members report booked sessions missing from **My bookings**, duplicate booking/idempotency, `Unknown product/program`, cancel `not_found`, or session buttons not changing to **Booked**.

## Symptoms that share one data-flow

- `POST /claims` appears successful but **My bookings** is empty or shows `Unknown product`, `Unknown program`, `Session time TBD`, `0 / 0 booked`.
- Cancel from My bookings shows `not_found` or a generic error banner.
- A member can click Book/Reserve repeatedly and consume multiple seats in the same session.
- Session cards still show Book/Reserve after the current member already booked.

## Investigation recipe

1. Confirm claims exist for the signed-in user:

```sql
SELECT vc.id, vc.voucher_id, vc.subscription_id, vc.session_id, vc.claimant_id,
       vc.created_at, vc.cancelled_at, s.product_id, p.name AS product,
       pg.name AS program, s.start_time, s.capacity, s.taken
FROM voucher_claims vc
JOIN program_members pm ON pm.id = vc.claimant_id
JOIN users u ON u.id = pm.user_id
LEFT JOIN sessions s ON s.id = vc.session_id
LEFT JOIN products p ON p.id = s.product_id
LEFT JOIN programs pg ON pg.id = p.program_id
WHERE lower(u.email) = lower(?)
ORDER BY vc.created_at DESC;
```

2. Probe the live route with the same user context and inspect actual JSON, not the UI fallback text:

```bash
curl -s -H 'Host: komuna.ahsanworks.com' \
  -H 'X-Komuna-User: <user_id>' \
  http://127.0.0.1/api/v1/my/bookings | python3 -m json.tool
```

3. If DB rows are rich but API objects contain blank IDs/null session fields, inspect the scanner used by the bookings query. A common bug is selecting joined booking columns but reusing a base claim scanner that only scans the first claim fields and ignores `Scan` errors.

4. Check duplicate claims for idempotency failures:

```sql
SELECT vc.claimant_id, vc.session_id, COUNT(*) AS claims
FROM voucher_claims vc
WHERE vc.cancelled_at IS NULL
GROUP BY vc.claimant_id, vc.session_id
HAVING COUNT(*) > 1;
```

5. For cancel failures, verify the frontend is not sending an empty claim ID. If `/my/bookings` returned `id: ""`, cancel may hit `/claims//cancel` or the wrong route. Also verify `claimByID` scans nullable columns with `sql.NullString`; subscription-backed claims often have `voucher_id IS NULL`.

## Minimal root fixes

- Add a dedicated booking DTO/scanner for `/my/bookings` that scans all selected joined columns and returns `product_name`, `program_name`, `session_start_time`, `session_end_time`, `session_capacity`, `session_taken`, and a non-empty claim `id`.
- Never ignore `rows.Scan` errors in booking/list handlers; return/log `db_err` or skip explicitly with evidence.
- In `POST /claims`, guard before insert/update: if the same `claimant_id` already has an uncancelled claim for the same `session_id`, return the existing claim or a clear already-booked response. Do this before incrementing `sessions.taken`.
- Enforce capacity and duplicate guard in the same transaction as `sessions.taken` increment and claim insert.
- Fix `claimByID` nullable scans (`voucher_id`, `subscription_id`, `alias`, `cancellation_reason`, `cancelled_at`) so subscription-backed claims do not serialize as `null` whole responses.
- Expose current-user booking state on session list DTOs (`is_booked`, `claim_id`) so the frontend can disable the action and render **Booked**.
- Standardize member-facing session action copy to **Book** unless the product spec says otherwise.
- Remove or justify any My Bookings `Vouchers` tab; if kept, tie it to compensation-voucher UX and working endpoint tests.

## Regression checks

- `/my/bookings` for a user with a subscription-backed claim returns the claim id and product/program/session fields.
- Reposting `POST /claims` for the same member/session does not create a second active claim and does not increment `sessions.taken` again.
- Cancelling a subscription-backed claim returns JSON for that claim, not `null` or `not_found`.
- Session list for the booked user returns `is_booked: true` / `claim_id`, and the UI shows a disabled **Booked** state.
