# Komuna: Drizzle/Postgres → Go/SQLite Relational Migration

Session: 2026-07-01 — Replaced JSON-blob `app_state` pattern with full 25-table relational schema.

## Canonical source

`/home/ubuntu/projects/komuna/apps/api/src/db/schema.ts` — Drizzle ORM (19 tables, 16 PG enums, 30+ indexes)
`/home/ubuntu/projects/komuna/apps/api/drizzle/0000_shiny_the_order.sql` — Raw PG migration

## Target

`/home/ubuntu/projects/komuna/api/v1/main.go` — Single-file Go API with SQLite (modernc.org/sqlite)

## Tables created (25 total)

### Core domain (matching Drizzle)
1. `users` — mirrors auth_users, also supports Neon Auth users
2. `platform_admins` — super admin flag
3. `programs` — name, description, visibility (public/need_approval/invitation_only/private), timezone, location, image_url, slug, category, image_tone, image_label, member_count, rating, sessions_per_week, featured
4. `program_members` — user_id → users, program_id → programs, status (active/pending/banned/inactive/left)
5. `program_member_roles` — program_member_id → program_members, role TEXT, product_id → products (nullable)
6. `program_invitations` — email, phone, token, status (pending/accepted/expired/revoked)
7. `products` — program_id → programs, name, description, type (session/simple), capacity, booking_window_days, cancellation_tiers JSON, image_url, status
8. `product_managers` — program_member_id, product_id, UNIQUE
9. `purchase_packages` — program_id, name, price, status, version, supersedes_id (self-ref)
10. `package_entries` — package_id, product_id, quantity, benefit_type (voucher/subscription), validity_type, validity_value
11. `custom_fields` — product_id, name, required
12. `purchases` — program_member_id, total_amount, status (pending/paid/failed/cancelled/refunded), xendit_invoice_id, invoice_url
13. `purchase_items` — purchase_id, package_id
14. `vouchers` — program_member_id, product_id, purchase_id, source (purchase/compensation/giveaway), status (active/claimed/expired/refunded), expired_at
15. `subscriptions` — program_member_id, program_id, product_id (nullable), purchase_id, status, started_at, expires_at
16. `sessions` — product_id, title, start_time, end_time, coach, status (scheduled/cancelled/completed), is_active, capacity, taken
17. `session_templates` — product_id UNIQUE, weekly_slots JSON
18. `session_managers` — session_id, program_member_id, UNIQUE
19. `voucher_claims` — voucher_id / subscription_id (mutually exclusive), session_id, claimant_id, alias, attendance_status, cancellation_reason
20. `custom_field_answers` — claim_id, field_id, value

### Auth (local email/password)
21. `auth_users` — id, email, name, password_hash
22. `auth_sessions` — token, user_id, expires_at

### Platform
23. `platform_settings` — service_fee_percentage, minimum_fee_amount, usd_to_idr_rate
24. `requests` — join/booking requests (program_id, product_id, session_id, user_id, request_type, status)
25. `notifications` — recipient_id, program_id, event_type, channel, title, body, read_at

### Additional infrastructure tables
26. `audit_logs` — program_id, actor_id, action, target_type, target_id, reason

## Key type mapping decisions

| PG/Drizzle | SQLite | Go Scan |
|-----------|--------|---------|
| `boolean` | `INTEGER` (0/1) | `int` then `!= 0` |
| `jsonb` | `TEXT` (JSON string) | `string`, parsed in app |
| `uuid` | `TEXT` | `string` |
| `timestamptz` | `TEXT` (RFC3339) | `string` |
| PG enums | `TEXT` with `CHECK` | `string` |
| `SERIAL` | n/a (use string IDs) | `string` |
| `decimal` | `TEXT` | `string` (stored as text for precision) |

## Critical bugs encountered

1. **NULL→string scan**: `image_url`, `description`, `location`, `slug` are nullable in seed but scanned as Go `string`. Fix: `COALESCE(col,'')` in queries.
2. **bool scan**: `featured` is INTEGER but scanned as `bool`. Fix: scan as `int`, convert.
3. **SetMaxOpenConns(1) deadlock**: workspace handler iterates program members, then queries roles in loop body — inner query blocks. Fix: `SetMaxOpenConns(10)`.
4. **UNIQUE with expression**: `UNIQUE(..., COALESCE(product_id,'__null__'))` fails in SQLite. SQLite treats NULLs in UNIQUE as distinct by default, so `UNIQUE(..., product_id)` works correctly for nullable columns.

## Seed data

Seeded on first run (`SELECT COUNT(*) FROM programs` = 0):
- 2 programs (Jakarta Fight Club, Bali Sunrise Yoga)
- 4 products (Boxing Fundamentals, Personal Training, Vinyasa Flow, Meditation Circle)
- 4 packages with entries (10-session, 20-session, 5-class intro, monthly unlimited)
- 3 sessions (relative to current time)
- Platform settings defaults

Re-seed: delete `sqlite.db` → restart service.
