# Session Booking Data Flow (V2 Relational Schema)

How vouchers, claims, and session capacity connect in the Go+SQLite API.

## Schema

```
vouchers (id, program_member_id, product_id, purchase_id, source, status, expired_at)
    ↓ voucher_claims (voucher_id → vouchers.id)
voucher_claims (id, voucher_id, session_id, claimant_id, attendance_status, alias)
    ↓ session_id → sessions.id
sessions (id, product_id, capacity, taken, coach, start_time, end_time, is_active)
```

## Booking Flow

1. **Member gets a voucher** — via purchase (`source='purchase'`), compensation (`source='compensation'`), or giveaway (`source='giveaway'`). Voucher is scoped to `program_member_id` + `product_id`. Status starts as `active`.

2. **Member claims a session** — creates a `voucher_claims` row linking the voucher to a session. The voucher's status changes to `claimed`.

3. **Session capacity** — `sessions.taken` should reflect `COUNT(voucher_claims WHERE session_id = X)`. The Go API may or may not maintain this automatically; when doing direct DB inserts, update it manually.

## Pre-filling a Session (DB-level)

Use this when you need to add bookings to a session for testing without going through the purchase UI.

```sql
-- 1. Identify the session
SELECT id, product_id, capacity, taken, coach, start_time FROM sessions WHERE id = 'ses-XXXX';

-- 2. Find members in the program who need vouchers
SELECT pmm.id, u.email, u.name
FROM program_members pmm JOIN users u ON pmm.user_id = u.id
WHERE pmm.program_id = 'prog-XXXX' AND pmm.status = 'active';

-- 3. Check existing vouchers for the product
SELECT v.id, v.program_member_id, v.status FROM vouchers v
WHERE v.product_id = 'prod-XXXX' AND v.status = 'active';

-- 4. For members without vouchers, create giveaway vouchers:
INSERT INTO vouchers (id, program_member_id, product_id, source, status, expired_at, created_at)
VALUES ('vch-NNNN', 'pm-XXXX', 'prod-XXXX', 'giveaway', 'active', '2026-09-01T00:00:00Z', datetime('now'));

-- 5. Create claims:
INSERT INTO voucher_claims (id, voucher_id, session_id, claimant_id, created_at)
VALUES ('clm-NNNN', 'vch-NNNN', 'ses-XXXX', 'pm-XXXX', datetime('now'));

-- 6. Mark vouchers claimed:
UPDATE vouchers SET status = 'claimed' WHERE id = 'vch-NNNN';

-- 7. Update session taken count:
UPDATE sessions SET taken = (SELECT COUNT(*) FROM voucher_claims WHERE session_id = 'ses-XXXX')
WHERE id = 'ses-XXXX';
```

## ID Generation

IDs follow the pattern `prefix-NNNN` (zero-padded 4-digit sequential):
- Vouchers: `vch-XXXX`
- Claims: `clm-XXXX`
- Sessions: `ses-XXXX`

Get the next available ID:
```sql
SELECT MAX(CAST(SUBSTR(id, 5) AS INTEGER)) FROM vouchers;
```

## Safety

- Always stop the service before DB manipulation: `sudo systemctl stop komuna-api.service`
- Always backup: `cp sqlite.db sqlite.db.bak-<reason>`
- Use `PRAGMA foreign_keys=OFF` during bulk inserts
- Restart and verify: `sudo systemctl start komuna-api.service && curl http://127.0.0.1:8095/api/v1/health`
