---
name: komuna-operations
description: "Safe operational tasks for the Komuna Go+SQLite API: database state management, seeding, user recovery, service lifecycle, and deployment. Use when modifying Komuna's live database, seeding data, recovering lost accounts, or managing the Go API service."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [komuna, database, seeding, operations, go-api]
    related_skills: [komuna-daily-report]
---

# Komuna Operations

## Overview

Operational tasks for the Komuna project's Go+SQLite API at `/home/ubuntu/projects/komuna/`. Covers safe database state management, seeding, account recovery, service lifecycle, and deployment verification.

## Service Management

```bash
# Restart the API service (ports :8095 internally, :443 via nginx)
sudo systemctl restart komuna-api.service

# Check status
sudo systemctl status komuna-api.service

# Build and deploy
cd /home/ubuntu/projects/komuna/api/v1
go test ./... && go build -o ../server .
sudo systemctl restart komuna-api.service
```

Public URL: `https://komuna.ahsanworks.com/`

## CRITICAL: Database Safety Rules

**NEVER delete `sqlite.db` to re-seed.** This wipes all auth_users, auth_sessions, members, vouchers, claims, purchases, and any runtime data. The user WILL lose accounts they created and will be unable to log in. Instead, always **merge data into the live database** using Python/SQLite DELETE+INSERT patterns, never `rm`.

### Schema Versions

The API has two schema generations. Know which one you're working with before touching the DB:

**V2 (current — relational schema):** `main.go` is ~2240 lines. Separate tables for every entity:
- `programs`, `products`, `users`, `auth_users`, `program_members`, `program_member_roles`, `product_managers`
- `purchase_packages`, `package_entries`, `sessions`, `vouchers`, `voucher_claims`, `subscriptions`
- `purchases`, `purchase_items`, `session_templates`, `session_managers`
- `requests`, `audit_logs`, `notifications`, `platform_settings`, `platform_admins`
- `custom_fields`, `custom_field_answers`, `program_invitations`

**V1 (legacy — `app_state` JSON blob):** `main.go` is ~1700 lines. A single `app_state` table with one row containing the entire state as JSON.

To determine the version: check if `app_state` table exists:
```sql
SELECT name FROM sqlite_master WHERE type='table' AND name='app_state';
```
If it returns a row → V1. If not (and there are 25+ tables instead) → V2.

### V2 Safe Pattern: DELETE + INSERT in relational tables

```python
# Disable FK during bulk seed to avoid cascade issues
con.execute("PRAGMA foreign_keys=OFF")

# Delete seed data in dependency order (children first)
for t in ["voucher_claims","custom_field_answers","subscriptions","vouchers",
           "purchases","purchase_items","session_managers","session_templates",
           "sessions","package_entries","purchase_packages",
           "product_managers","custom_fields","products",
           "program_member_roles","program_members","program_invitations",
           "requests","audit_logs","notifications","programs"]:
    con.execute(f"DELETE FROM {t}")

# Insert programs (use INSERT, not INSERT OR REPLACE)
for p in all_progs:
    con.execute("INSERT INTO programs(id,name,description,...) VALUES(?,?,?,...)",
                (p["id"], p["name"], p["desc"], ...))

# Insert products (each references a program_id)
for p in all_products:
    con.execute("INSERT INTO products(id,program_id,name,...) VALUES(?,?,?,...)",
                (p["id"], p["pid"], p["name"], ...))

# Insert users + auth_users (both tables must have matching IDs)
for email, name in user_names.items():
    uid = f"user-{hash(email) & mask:016x}"
    con.execute("INSERT OR IGNORE INTO users(id,email,name,created_at) VALUES(?,?,?,?)", ...)
    con.execute("INSERT OR IGNORE INTO auth_users(id,email,name,password_hash,created_at) VALUES(?,?,?,?,?)", ...)

# Insert program_members + roles + product_managers
for prog_id, roles, status in member_spec:
    pmid = gen_id("pm")
    con.execute("INSERT INTO program_members(id,user_id,program_id,status,joined_at) VALUES(...)", ...)
    for role in roles:
        con.execute("INSERT INTO program_member_roles(id,program_member_id,role) VALUES(...)", ...)
    # Manager roles get product_managers entries too
    if "manager" in roles:
        for prod_id in manager_products[email][prog_id]:
            con.execute("INSERT INTO product_managers(id,program_member_id,product_id) VALUES(...)", ...)

con.commit()
```

Then restart the service: `sudo systemctl restart komuna-api.service`

### V1 (Legacy) Safe Pattern: Read-Modify-Write app_state via Python

```python
import sqlite3, json
from datetime import datetime, timezone

con = sqlite3.connect('sqlite.db')

# OPTIONAL: Force WAL checkpoint to merge pending writes into main DB
con.execute('PRAGMA wal_checkpoint(TRUNCATE)')

# Read current state
row = con.execute("SELECT payload FROM app_state WHERE id=1").fetchone()
state = json.loads(row[0])

# Modify (e.g., add programs)
state['Programs'].append({...})

# Write back — use compact JSON to match Go output
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
con.execute("UPDATE app_state SET payload=?, updated_at=? WHERE id=1",
            (json.dumps(state, separators=(',', ':')), now))
con.commit()
con.close()
```

Then restart the service: `sudo systemctl restart komuna-api.service`

### Adding Seed Programs Without Damage (V1 Legacy)

**This applies only to the V1 `app_state` JSON blob API.** For V2 relational, use the DELETE+INSERT pattern in the V2 section above.

1. Read current programs from live DB via `curl http://127.0.0.1:8095/api/v1/programs`
2. Identify which programs need adding (check by ID)
3. Use the Python read-modify-write pattern above to insert only missing programs
4. Restart service
5. Verify via `curl http://127.0.0.1:8095/api/v1/programs | python3 -c "import json,sys; print(len(json.load(sys.stdin)['data']))"`

### WAL Checkpointing (V1 Legacy)

**V1 only.** When the Go service was running the V1 `app_state` API, SQLite WAL mode meant recent writes lived in `sqlite.db-wal`, not the main file. Always run `PRAGMA wal_checkpoint(TRUNCATE)` before reading from Python to get the full current state. V2's relational schema with multiple tables doesn't typically need this for reads.

## Auth System

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/auth/sign-up` | Register |
| POST | `/api/v1/auth/sign-in` | Login |
| GET | `/api/v1/auth/session` | Check session |
| POST | `/api/v1/auth/sign-out` | Logout |

### Password Hashing (Go implementation reproduced in Python)

The Go API uses a custom salted SHA256 hash with 120,000 iterations:

```python
import hashlib, secrets

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)  # 32 hex chars
    buf = (salt + ":" + password).encode()
    for _ in range(120000):
        buf = hashlib.sha256(buf).digest()
    return f"{salt}:{buf.hex()}"
```

Format stored in `auth_users.password_hash`: `hex_salt:hex_digest`

### Recovering a Lost User Account

When the DB was accidentally wiped and a user can't log in:
1. Hash a temporary password using the Python function above
2. Insert into `auth_users`:
   ```sql
   INSERT INTO auth_users(id, email, name, password_hash, created_at)
   VALUES (?, ?, ?, ?, ?)
   ```
3. Add a member record in `app_state.payload["Members"]` for their programs
4. Tell the user their temp password and instruct them to change it immediately

## Project Structure

```
/home/ubuntu/projects/komuna/
├── api/v1/main.go       # Go API — single-file, ~2240 lines (V2 relational schema)
├── api/v1/main_test.go  # Tests
├── api/server           # Compiled binary
├── sqlite.db            # Live database (DO NOT DELETE, DO NOT rm -f)
├── sqlite.db.bak-*      # Backups created before seed operations
├── apps/api/            # Cloudflare Worker (TypeScript, separate deployment)
├── apps/web/            # React SPA (Vite)
│   ├── .env             # Build-time env vars (VITE_ prefixed — see pitfall below)
│   ├── dist/            # Production build output
│   └── .env.example     # Template (does NOT include VITE_USD_TO_IDR_RATE)
└── docs/                # Project documentation
```

## Frontend Build & Deploy

```bash
cd /home/ubuntu/projects/komuna/apps/web

# Build (tsc + vite build)
npm run build

# Deploy to nginx static dir
sudo rsync -a --delete dist/ /var/www/html/projects/komuna/
sudo chown -R www-data:www-data /var/www/html/projects/komuna/
```

The frontend is served by nginx from `/var/www/html/projects/komuna/` at the path prefix `/projects/komuna/`. The Vite build reads env vars from `apps/web/.env`, NOT from the root `/home/ubuntu/projects/komuna/.env`.

### Vite Env Var Pitfall

**CRITICAL:** Vite only exposes env vars prefixed with `VITE_` to client code (`import.meta.env`). The root `.env` has variables like `USD_TO_IDR_RATE=16000` — these are for the Go API, NOT accessible to the frontend. If a frontend feature depends on a build-time value:

1. The var MUST be in `apps/web/.env` (not root `.env`)
2. The var MUST be prefixed with `VITE_` (e.g., `VITE_USD_TO_IDR_RATE=16000`)
3. Rebuild and redeploy after adding/changing

**Symptom of this bug:** Currency conversion (IDR → USD) silently does nothing — `getUsdToIdrRate()` returns 0, the `if (rate)` guard skips conversion, prices display in IDR amounts with USD currency symbols (e.g., "$425,000" instead of "$26.56").

### Linked Files

- `scripts/hash_password.py` — standalone script to hash a password matching Go API's algorithm. Run directly: `python3 scripts/hash_password.py somepassword`
- `references/v2-schema.md` — complete V2 relational schema reference (tables, columns, FK relationships, seeding pattern, role assignment)
- `references/session-booking-flow.md` — pre-filling sessions with bookings: voucher → claim → sessions.taken data flow and SQL patterns
- `references/manager-dashboard.md` — Go API manager dashboard implementation: route handler, data flow, timezone handling, response shape, and `countAttendance` helper

### External Seed Scripts

- `/tmp/komuna-reseed-v2.py` — full 40-user, 25-program seed script for the V2 relational schema. Run with: `sudo systemctl stop komuna-api.service && python3 /tmp/komuna-reseed-v2.py && sudo systemctl start komuna-api.service`

## Full-State Reseeding (Complete DB Replacement)

When the user provides a full spec (users + programs + memberships + roles), write a Python script that populates all relevant tables. The approach differs by schema version.

### V2 Relational Schema Seed Script

For the current V2 relational schema, always:
1. `PRAGMA foreign_keys=OFF` before DELETE operations
2. Delete seed data in dependency order (children before parents)
3. Insert programs, products, users, auth_users, program_members, roles, product_managers
4. Insert packages, sessions, vouchers, requests as needed
5. Restart the service: `sudo systemctl restart komuna-api.service`
6. Verify with curl health check + programs endpoint + login test + workspace test

See `scripts/komuna-reseed-v2.py` for a working 40-user, 25-program seed script with the full relational schema pattern.

### V1 (Legacy) app_state JSON Seed Script

For the V1 `app_state` JSON blob API: build the entire `app_state` payload and populate `auth_users`. The script must produce JSON that Go's `json.Unmarshal` can deserialize into the `State` struct.

### JSON Type Pitfalls (V1 Legacy — Go `app_state` JSON → Python)

These Go struct fields will cause silent `load_failed` 500 errors if the JSON types don't match:

| Go Type | Go JSON Key | Correct Python | WRONG Python |
|---------|------------|----------------|-------------|
| `*int` | `ValidityValue` | `30` (integer) | `"30"` (string) |
| `Role` struct | `"role"`, `"product_id"` | lowercase keys | `"Role"`, `"ScopedProductID"` |
| `Package.SupersedesID` | `SupersedesID` | `""` (empty string) | missing key |
| `[]Purchase` | `Purchases` | `[]` or `"Purchases":[]` | missing key entirely |

### Full Seed Script Template

See `scripts/komuna-reseed.py` for a working 40-user, 25-program seed script. **Always stop the service first and back up the DB before running.** Key patterns:
- Password hashing: use `scripts/hash_password.py` or inline the algorithm
- Always include all state keys even if empty: `Purchases: []`
- Use `json.dumps(state, separators=(',', ':'))` for compact output matching Go
- Build `auth_users` and `app_state` in the same script, then restart the service

### Debugging `load_failed` Errors

When the Go API returns 500 with `{"error":"load_failed"}` after a manual DB update:

1. **Test with minimal state first**: Replace the payload with an empty state (`all lists empty, Settings with required fields`). If that loads, the schema is fine — the problem is a specific field.
2. **Incrementally add complexity**: Add programs, then members, then products — test after each step to isolate the offending JSON.
3. **Check Go struct tags**: Compare your JSON keys against Go struct field names and explicit `json:"..."` tags. Go's default serialization uses TitleCase; only structs with explicit tags diverge.
4. **Temporary debug logging**: Add `log.Printf` to the `load()` function (line ~230 in `main.go`) to see the unmarshal error, then `go build`, redeploy, test, and remove the debug logging.

### Python Date Helpers

```python
from datetime import datetime, timezone, timedelta
t = datetime.now(timezone.utc)
ts = lambda h_offset=0: (t + timedelta(hours=h_offset)).strftime('%Y-%m-%dT%H:%M:%SZ')
# NEVER: t.replace(hour=t.hour+h_offset) — fails when offset crosses midnight
now_str = lambda: datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
```

## Common Issues & Troubleshooting

### ⚠️ Dual-Stack Architecture (Go + Cloudflare Workers)

The Komuna project has **two API stacks**:

| Stack | Location | Status | API Prefix |
|-------|----------|--------|------------|
| **Go+SQLite** | `api/v1/main.go`, port 8095 | **Production** (served by nginx) | `/api/v1/`, `/projects/komuna/api/v1/` |
| **Cloudflare Workers** | `apps/api/src/` (Hono+Drizzle+NeonDB) | NOT deployed here (Cloudflare-hosted) | Depends on `VITE_API_BASE_URL` |

The frontend (`apps/web/`) hits whichever API `VITE_API_BASE_URL` points to. When debugging API issues:
- Check `apps/web/.env` for the active `VITE_API_BASE_URL`
- The Go API uses custom auth (salted SHA256), the Worker API uses Neon Auth
- DB state lives in different places (local `sqlite.db` vs NeonDB Postgres)
- **Before touching the Go DB, verify which stack the frontend is configured to hit**

**🚨 CRITICAL PITFALL — Feature implementation MUST target the Go API first.** This server runs the Go API on port 8095, nginx proxies `/api/v1/` to it. The Cloudflare Worker at `apps/api/src/` is a separate deployment that is NOT running on this machine. When asked to implement a backend feature, always modify `api/v1/main.go` (the Go API), NOT `apps/api/src/` (the Worker). Modifying the Worker code has zero effect on production — the Go API is the one serving real traffic. The Worker API is a future migration target, not the current live backend.

**Double-check:** If you catch yourself editing TypeScript files in `apps/api/src/` for a feature that should go live, stop — you need to edit `api/v1/main.go` instead. The frontend at `apps/web/` connects to the Go API via nginx; the Worker is not in the request path for this deployment.

### Attendance CRUD Buttons Not Working

**Symptom:** Attended/No-show toggle buttons on the manager dashboard flash a loading spinner briefly but don't persist. Alias edit works fine. No console errors.

#### Production Stack (Go API — `api/v1/main.go`)

This is the **more common scenario** since the production nginx proxies `/api/v1/` to the Go API on port 8095.

**Root cause:** The Go API's `sessionTree` function at line 1599 was a **stub**: it returned a fake response without ever touching the database:
```go
// STUB — returned fake success without writing to DB
jsonOut(w, map[string]any{"claim_id": "", "session_id": sid, "attendance_status": "present", "marked_at": now(), "method": "manual"})
```
The frontend sends `POST /sessions/:id/attendance/override` → stub returns HTTP 200 with fake data → frontend calls `fetchData()` to refresh → DB was never updated → old status reappears.

**Fix:** Implement real body parsing and DB update in `sessionTree`:
```go
if len(parts) >= 2 && parts[1] == "attendance" {
    // /override sub-path for manual status changes
    if len(parts) >= 3 && parts[2] == "override" {
        var in struct {
            ClaimID   string `json:"claim_id"`
            NewStatus string `json:"new_status"`
        }
        json.NewDecoder(r.Body).Decode(&in)
        a.db.Exec("UPDATE voucher_claims SET attendance_status=? WHERE id=? AND session_id=?", in.NewStatus, in.ClaimID, sid)
        jsonOut(w, map[string]any{"claim_id": in.ClaimID, "session_id": sid, "attendance_status": in.NewStatus})
        return
    }
    // Base /attendance — marks present (QR/manual flow)
    var in struct { ClaimID string `json:"claim_id"`; Method string `json:"method"` }
    json.NewDecoder(r.Body).Decode(&in)
    a.db.Exec("UPDATE voucher_claims SET attendance_status='present' WHERE id=? AND session_id=?", in.ClaimID, sid)
    jsonOut(w, map[string]any{"claim_id": in.ClaimID, "session_id": sid, "attendance_status": "present"})
    return
}
```

**Pitfall — `claimByID` returns nil:** The `claimByID` helper function uses `rows.Scan` into plain `string` fields, which fails silently when `cancelled_at` is NULL (see "Go `rows.Scan` Silent Failure" below). Do NOT call `claimByID` in attendance responses — return a synthetic JSON response instead (the frontend doesn't use the claim detail, it calls `fetchData()` separately).

**Test:** `curl -X POST http://127.0.0.1:8095/api/v1/sessions/<sid>/attendance/override -H 'Content-Type: application/json' -d '{"claim_id":"clm-xxx","new_status":"present"}'` → verify DB updated: `sqlite3 sqlite.db "SELECT attendance_status FROM voucher_claims WHERE id='clm-xxx'"`.

#### Worker API Stack (`apps/api/src/`)

**Root cause (different):** Frontend `apiClient.markAttendance()` sends `{ claim_id, status }` to `POST /sessions/:id/attendance`, but the Worker API Zod validator expects `{ claim_id, method: 'qr_scan' | 'manual' }`. Zod strips unknown fields silently — no error, no network failure, just no data change.

Additionally, the `markAttendance` service always sets status to `'present'` (for QR/mobile flow), so `'absent'` would be wrong even if the payload matched.

**Fix:** Route to `POST /sessions/:id/attendance/override` with `{ claim_id, new_status }` instead. This endpoint accepts both `'present'` and `'absent'` and has no `already_marked` guard.

**Files (Worker stack):**
- Frontend: `apps/web/src/lib/api.ts` — `markAttendance` method (change endpoint path + payload)
- Backend validator: `apps/api/src/validators/attendance.ts` — `markAttendanceBodySchema` vs `overrideAttendanceBodySchema`
- Backend service: `apps/api/src/services/attendance.ts` — `markAttendance` vs `overrideAttendance`

### Dashboard Shows "No assigned products" for Managers

**Symptom:** Manager logs in, navigates to a program, sees "No assigned products are available for this program."

**Root cause:** The workspace handler (`/me/workspace`) reads manager product assignments from `program_member_roles.product_id`, NOT from the `product_managers` table. If `program_member_roles` has `role='manager'` but `product_id IS NULL`, the workspace returns roles without `productId` → frontend shows empty state.

**Check:**
```sql
-- Manager roles with NULL product_id (these are broken)
SELECT pmr.id, pmr.program_member_id, pmr.product_id, u.email
FROM program_member_roles pmr
JOIN program_members pmm ON pmr.program_member_id = pmm.id
JOIN users u ON pmm.user_id = u.id
WHERE pmr.role = 'manager' AND (pmr.product_id IS NULL OR pmr.product_id = '');

-- Compare against product_managers (which has the real assignments)
SELECT pm.program_member_id, pm.product_id, u.email
FROM product_managers pm
JOIN program_members pmm ON pm.program_member_id = pmm.id
JOIN users u ON pmm.user_id = u.id;
```

**Fix:** Backfill `program_member_roles.product_id` from `product_managers` where the manager role's `product_id` is NULL. One `program_member` can manage multiple products — each gets its own `program_member_roles` row with the specific `product_id`.

**⚠ Multi-product pitfall:** If a manager has 1 row in `program_member_roles` (with NULL product_id) but 2 rows in `product_managers` (prod-A, prod-B), do NOT just UPDATE the single role row. That would only cover one product — the other stays invisible. Instead:

```sql
-- Step 1: UPDATE the existing NULL row for the first product
UPDATE program_member_roles
SET product_id = (SELECT product_id FROM product_managers WHERE program_member_id = ? LIMIT 1)
WHERE program_member_id = ? AND role = 'manager' AND product_id IS NULL;

-- Step 2: INSERT new rows for any additional products (skip the first)
INSERT INTO program_member_roles (id, program_member_id, role, product_id)
SELECT 'pmr-' || printf('%04x', abs(random()) % 65536),
       pm.program_member_id, 'manager', pm.product_id
FROM product_managers pm
WHERE pm.program_member_id = ?
  AND pm.product_id NOT IN (
    SELECT product_id FROM program_member_roles
    WHERE program_member_id = pm.program_member_id AND role = 'manager'
  );
```

Run the check query again after the fix — zero rows with NULL product_id means success.

### Pre-filling Sessions with Bookings

When testing requires booked members in a session, create voucher_claims directly. See `references/session-booking-flow.md` for the complete data flow and SQL patterns (vouchers → claims → sessions.taken).

Quick pattern:
1. Find or create giveaway vouchers for members scoped to the session's product
2. Create `voucher_claims` rows linking vouchers to the session
3. Mark vouchers `claimed`
4. Update `sessions.taken` to match claim count
5. Always stop service + backup DB first

### Go `rows.Scan` Silent Failure with SQLite NULL Columns

**Symptom:** API endpoint returns some fields populated (e.g., `id`, `voucher_id`) but ALL subsequent columns are empty/null (e.g., `member_name: null`, `member_email: ""`, `member_id: ""`). The DB query run directly in sqlite3 returns correct data, but the API response is empty.

**Root cause:** Scanning a SQLite NULL value into a plain Go `string` variable causes `rows.Scan` to fail silently **for all remaining columns**. If column 5 (`alias`) is NULL, columns 6–12 (`attendance_status`, `cancelled_at`, ..., `member_name`) all stay at their zero values (empty string). Because the Go code at `main.go:1162` ignores the `rows.Scan` error return, this failure is invisible — the row is still appended to the array with empty fields.

**Check:** Scan errors are silent when the error return is dropped:
```go
// BROKEN — ignores scan error, silent corruption
rows.Scan(&id, &vid, &subID, &sessionID, &alias, &att, &cancelled, ...)
```

**Fix:** Use `sql.NullString` for all nullable columns AND check the error:
```go
// FIXED — sql.NullString for nullable columns, error check
var subID, alias, att, cancelled sql.NullString
if err := rows.Scan(&id, &vid, &subID, &sessionID, &alias, &att, &cancelled, ...); err != nil {
    continue  // skip rows that fail scan
}
attendance := "pending"
if att.Valid && att.String != "" {
    attendance = att.String
}
```

**Affected columns** (any of these being NULL silently corrupts all columns scanned after them): `vc.alias`, `vc.attendance_status`, `vc.cancelled_at`, `vc.subscription_id`.

**Practical consequence:** `claimByID()` (line 1827) returns `nil` for most claims because `cancelled_at` is commonly NULL. When writing new endpoint code, avoid calling `claimByID` — construct a synthetic JSON response instead. Only use it for claims you know have non-NULL `cancelled_at`.

**Debugging approach:** Add a one-line `log.Printf` after the scan to see if values are populated, then rebuild + restart + curl. If the log shows empty strings but sqlite3 shows real data, the scan is failing on a nullable column earlier in the list.

### Verification Checklist

- [ ] `go test ./...` passes before deploying
- [ ] `go build -o ../server .` succeeds
- [ ] `sudo systemctl restart komuna-api.service` completes
- [ ] Internal health: `curl -sS http://127.0.0.1:8095/api/v1/health`
- [ ] Public programs: `curl -sS https://komuna.ahsanworks.com/api/v1/programs`
- [ ] Login test: sample user via `POST /api/v1/auth/sign-in`
- [ ] Workspace test: `GET /api/v1/me/workspace` with Bearer token for role verification
- [ ] Git committed and pushed after meaningful changes
- [ ] Database was NOT deleted — only modified via Python/SQLite if needed
