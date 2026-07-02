# Komuna V2 Relational Schema Reference

The Go API (`main.go` ~2240 lines) uses a proper relational SQLite schema instead of the V1 `app_state` JSON blob.

## Key Tables

### Core Entities
- **programs** — id PK, name, description, visibility (public|need_approval|invitation_only|private), timezone, location, category, image_tone, image_label, member_count, rating, sessions_per_week, featured (0|1), created_at
- **products** — id PK, program_id FK→programs, name, description, type (session|simple), capacity, booking_window_days, status (active|archived), created_at
- **users** — id PK, email, name, created_at
- **auth_users** — id PK, email UNIQUE, name, password_hash, created_at (separate from users table)

### Membership & Roles
- **program_members** — id PK, user_id FK→users, program_id FK→programs, status (active|pending|banned|inactive|left), joined_at, UNIQUE(user_id,program_id)
- **program_member_roles** — id PK, program_member_id FK→program_members, role TEXT, product_id FK→products (nullable), UNIQUE(program_member_id,role,product_id)
- **product_managers** — id PK, program_member_id FK→program_members, product_id FK→products, UNIQUE(program_member_id,product_id)

### Packages & Purchases
- **purchase_packages** — id PK, program_id FK→programs, name, price, status (active|archived), version, supersedes_id, created_at
- **package_entries** — id PK, package_id FK→purchase_packages, product_id FK→products, quantity, benefit_type (voucher|subscription), validity_type (days_from_purchase|end_of_purchase_month|end_of_n_months), validity_value
- **purchases** — id PK, program_member_id FK→program_members, total_amount, status (pending|paid|failed|cancelled|refunded), created_at
- **purchase_items** — id PK, purchase_id FK→purchases, package_id FK→purchase_packages

### Sessions
- **sessions** — id PK, product_id FK→products, title, start_time, end_time, coach, status (scheduled|cancelled|completed), is_active, capacity, taken
- **session_templates** — id PK, product_id UNIQUE FK→products, weekly_slots JSON, created_at, updated_at
- **session_managers** — id PK, session_id FK→sessions, program_member_id FK→program_members

### Vouchers & Claims
- **vouchers** — id PK, program_member_id FK→program_members, product_id FK→products, purchase_id FK→purchases, source (purchase|compensation|giveaway), status (active|claimed|expired|refunded), expired_at, created_at
- **subscriptions** — id PK, program_member_id FK→program_members, program_id FK→programs, product_id FK→products, purchase_id FK→purchases, status (active|expired|cancelled|refunded), started_at, expires_at
- **voucher_claims** — id PK, voucher_id FK→vouchers (nullable), subscription_id FK→subscriptions (nullable), session_id FK→sessions, claimant_id FK→program_members, alias, attendance_status (present|absent), created_at

### Platform
- **platform_settings** — id PK, service_fee_percentage, minimum_fee_amount, usd_to_idr_rate, updated_at
- **platform_admins** — id PK, user_id UNIQUE FK→users, created_at
- **requests** — id PK, program_id FK→programs, user_id FK→users, email, name, request_type (join|full_session|out_of_window), status (pending|approved|denied), created_at
- **audit_logs** — id PK, program_id FK→programs, actor_id FK→users, action, target_type, target_id, created_at
- **notifications** — id PK, recipient_id FK→users, program_id FK→programs, event_type, channel (email|push|sms), title, body, created_at
- **custom_fields** — id PK, product_id FK→products, name, required
- **custom_field_answers** — id PK, claim_id FK→voucher_claims, field_id FK→custom_fields, value

## Seeding Pattern

```python
# 1. Disable foreign keys during bulk operations
con.execute("PRAGMA foreign_keys=OFF")

# 2. Delete in dependency order (children before parents)
DELETE FROM voucher_claims; DELETE FROM subscriptions; DELETE FROM vouchers;
DELETE FROM purchases; DELETE FROM purchase_items;
DELETE FROM session_managers; DELETE FROM session_templates; DELETE FROM sessions;
DELETE FROM package_entries; DELETE FROM purchase_packages;
DELETE FROM product_managers; DELETE FROM custom_fields; DELETE FROM products;
DELETE FROM program_member_roles; DELETE FROM program_members;
DELETE FROM program_invitations;
DELETE FROM requests; DELETE FROM audit_logs; DELETE FROM notifications;
DELETE FROM programs;

# 3. Insert in reverse order (parents before children)
INSERT INTO programs ...;
INSERT INTO products ...;
INSERT INTO users ...;
INSERT INTO auth_users ...;
INSERT INTO program_members ...;
INSERT INTO program_member_roles ...;
INSERT INTO product_managers ...;  # for manager roles
INSERT INTO purchase_packages ...;
INSERT INTO package_entries ...;
INSERT INTO sessions ...;

# 4. Commit and restart
con.commit()
sudo systemctl restart komuna-api.service
```

## Role Assignment

Three tables work together for role-based access:

1. **program_members** — links user to program with status
2. **program_member_roles** — assigns roles: `member`, `admin`, `superadmin`, or `manager`
3. **product_managers** — scopes a `manager` role to specific products

For a user who is `manager` of a specific product:
- One row in `program_members` (status='active')
- Two rows in `program_member_roles`: `{role:'member'}` and `{role:'manager'}`
- One row in `product_managers` per managed product: `{program_member_id, product_id}`

## Verification

After seeding, always verify:
```bash
curl -s http://127.0.0.1:8095/api/v1/programs | python3 -c "import json,sys;print(len(json.load(sys.stdin)['data']))"
curl -s -X POST http://127.0.0.1:8095/api/v1/auth/sign-in -H 'Content-Type: application/json' -d '{"email":"aristoavilla@gmail.com","password":"komuna123"}'
```
