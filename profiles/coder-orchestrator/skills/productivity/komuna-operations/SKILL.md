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

### Mechanical Go API Refactors

When implementing an approved no-behavior-change split of `api/v1/main.go`:
1. Keep every new file in `api/v1/` as `package main`; do not create subdirectories or new packages.
2. Baseline first: `go test ./...` and `go build -o /tmp/komuna-refactor-check .` before moving code.
3. Move top-level declarations by responsibility only; preserve handler/function names and route registrations.
4. Use `goimports` after the split to assign imports per file (`go install golang.org/x/tools/cmd/goimports@latest` if missing).
5. Build the real deployed binary with `go build -o ../server .`, restart `komuna-api.service`, then verify local and public health plus a real data endpoint (for example `/api/v1/programs`).
6. Commit/push only the refactor files; leave unrelated untracked docs/uploads alone.


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
| GET | `/api/v1/auth/session` | Check session (now includes `profile_picture`) |
| POST | `/api/v1/auth/sign-out` | Logout |
| PUT | `/api/v1/profile/name` | Change display name |
| PUT | `/api/v1/profile/email` | Change email (requires password) |
| PUT | `/api/v1/profile/password` | Change password (requires current password, min 8 chars) |
| POST | `/api/v1/profile/picture` | Upload profile picture (multipart, 5MB max) |
| DELETE | `/api/v1/profile/picture` | Remove profile picture |

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

### Discovery Program Card CTA Changes

When the user asks to remove repetitive Join/Joined CTAs from discovery cards, make the smallest frontend-only change in `apps/web/src/components/discovery/ProgramCard.tsx`: remove the card-level join action/button and its now-unused imports/state, but keep the whole card clickable via `navigate(detailPath)` so joining still happens from the program detail page. Verify with `npm run test -- ProgramCard && npm run build`, deploy `apps/web/dist/` to `/var/www/html/projects/komuna/`, then commit/push.

### Mobile UI Fix Pattern: Program Detail / Responsive Pages

When fixing Komuna mobile layout issues after an approved review artifact, prefer the smallest CSS-led patch:
1. Add stable class hooks to existing inline-styled React elements instead of rewriting components.
2. Import one small page-scoped stylesheet from the page entry (`apps/web/src/pages/ProgramDetailPage.tsx` for program detail fixes).
3. Use media-query overrides to neutralize desktop inline styles (`grid-template-columns`, large `padding`, `min-height`, image `aspect-ratio`, large typography); `!important` is acceptable here because many current components use inline style props.
4. For guest-only sign-in prompts, keep desktop spacing as the base and compact through classes such as `guest-banner`, `guest-banner__content`, `guest-banner__icon`, `guest-banner__text`, and `guest-banner__button`. On narrow screens: reduce padding/icon/text, allow wrapping, and make the button full-width only around ≤420px.
5. For the program-detail "Upcoming sessions" column, desktop `SessionCardCompact` uses a 3-column grid (`148px` image + text + action). On mobile this can make titles/times wrap vertically. Fix in `apps/web/src/pages/program-detail/mobile.css` by overriding `.hero-sessions .session-card` to a compact 2-column grid (small image + text) and move the action/spots column to a full-width bottom row via `> :last-child { grid-column: 1 / -1; flex-direction: row !important; }`. This is smaller than rewriting the component.
6. Verify with the specific page test plus build (`npm run test -- ProgramDetailPage && npm run build`), deploy with rsync, then confirm the live CSS asset contains the new selectors and the public route returns 200.

This avoids over-refactoring while making oversized hero/session/guest-banner sections fit mobile screens.

### Vite Env Var Pitfall

**CRITICAL:** Vite only exposes env vars prefixed with `VITE_` to client code (`import.meta.env`). The root `.env` has variables like `USD_TO_IDR_RATE=16000` — these are for the Go API, NOT accessible to the frontend. If a frontend feature depends on a build-time value:

1. The var MUST be in `apps/web/.env` (not root `.env`)
2. The var MUST be prefixed with `VITE_` (e.g., `VITE_USD_TO_IDR_RATE=16000`)
3. Rebuild and redeploy after adding/changing

**Symptom of this bug:** Currency conversion (IDR → USD) silently does nothing — `getUsdToIdrRate()` returns 0, the `if (rate)` guard skips conversion, prices display in IDR amounts with USD currency symbols (e.g., "$425,000" instead of "$26.56").

### Build-Time vs Runtime Basename Pitfall

**CRITICAL:** The nginx config for `komuna.ahsanworks.com` injects two runtime overrides via `sub_filter` before `</head>`:

```
sub_filter '</head>' '<script>window.__BASENAME__="/";window.__API_BASE__="/api/v1"</script></head>';
```

This means:

| Value | Build-time (`import.meta.env`) | Runtime (nginx injection) |
|-------|-------------------------------|--------------------------|
| `BASE_URL` / `__BASENAME__` | `/projects/komuna/` | `/` |
| API base | `/projects/komuna/api/v1` | `/api/v1` |

The domain serves the SPA at the **root** (`/`), NOT under `/projects/komuna/`. The `sub_filter` also rewrites asset paths: `src="/projects/komuna/assets/..."` → `src="/assets/..."`.

**ANY frontend code that constructs absolute URLs using `import.meta.env.BASE_URL` will produce wrong paths on the production domain.** Always check `window.__BASENAME__` at runtime first:

```ts
function getRuntimeBase(): string {
  if (typeof window !== 'undefined' && (window as any).__BASENAME__) {
    return (window as any).__BASENAME__ as string
  }
  return import.meta.env.BASE_URL || '/'
}
```

**Known casualty:** `resolveSignedOutRoute()` in `apps/web/src/lib/logout.ts` used the build-time base to construct the post-logout redirect URL. It produced `/projects/komuna/auth/sign-in` on a domain where React Router has basename `/`, so the remaining path `projects/komuna/auth/sign-in` matched no route → NotFoundPage with "Page not found."

**Verification after fix:**
```bash
# Confirm the deployed JS reads runtime __BASENAME__
curl -s "https://komuna.ahsanworks.com/assets/$(curl -s https://komuna.ahsanworks.com/ | grep -oP 'assets/index-[^\"]+\.js')" | grep -o '__BASENAME__'
# Must return matches (shows the runtime check is present)

# Confirm the domain HTML injects __BASENAME__
curl -s "https://komuna.ahsanworks.com/" | grep -o 'BASENAME__=\"/\"'
# Must return BASENAME__="/" (nginx sub_filter injection is active)
```

### Linked Files

- `scripts/hash_password.py` — standalone script to hash a password matching Go API's algorithm. Run directly: `python3 scripts/hash_password.py somepassword`
- `references/v2-schema.md` — complete V2 relational schema reference (tables, columns, FK relationships, seeding pattern, role assignment)
- `references/session-booking-flow.md` — pre-filling sessions with bookings: voucher → claim → sessions.taken data flow and SQL patterns
- `references/manager-dashboard.md` — Go API manager dashboard implementation: route handler, data flow, timezone handling, response shape, and `countAttendance` helper
- `references/frontend-auth-guards.md` — React SPA auth architecture: session store, sign-out flow, protected route pattern, route audit of missing guards, and the "??"/"User" stale-render bug
- `references/restricted-route-auth-guards.md` — backend + frontend restricted-route auth guard pattern; avoid `currentUser()` fallback on account/dashboard APIs and add unauth 401 regression tests

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

### Program Cards/Detail Show Joined or Rejoin for Guests/New Users

**Symptom:** A guest or newly signed-up user sees discovery/program cards as “Joined”, or the program detail CTA says “Rejoin program” even though they have never joined. This may appear on discovery, search, and detail pages. It is usually an API DTO bug, not localStorage.

**Root causes:**
1. `api/v1/dto.go::programDTO()` hardcoded `membershipStatus: "active"` for every program instead of checking `program_members` for the current signed-in user.
2. Detail DTOs may hardcode `userRoles` (for example `[]string{"admin", "member"}`) even when `membershipStatus` is `null`. The frontend `HeroSection` treats `membershipStatus === null && userRoles.length > 0` as “previous member” and shows **Rejoin program**.
3. Program cards use the DTO `slug`. `programDTO()` can generate a slug from the program name when `programs.slug` is empty, but `programTree()` previously resolved only `id` or stored `slug`, so generated slugs 404.
4. The React session can consider the visitor a guest while the browser still has an old `komuna_session` cookie. If normal `apiClient` requests use browser credentials, the API can return joined/member data for what the UI treats as a guest, causing **Joined**, **Rejoin program**, **Book**, or **Leave Program** to appear incorrectly.

**Fix pattern:**
- Pass the real per-request membership status into `programDTO()` from list and detail handlers:
  ```go
  a.programDTO(p, cats, mc, rating, spw, feat != 0, true, a.programMembershipStatus(r, p.ID), nil)
  ```
- For detail responses, also pass real roles for the current authenticated user; guests and non-members must get `userRoles: []`:
  ```go
  a.programDTO(p, cats, mc, rating, spw, feat != 0, false, a.programMembershipStatus(r, p.ID), a.programUserRoles(r, p.ID))
  ```
- Implement `programMembershipStatus(r, pid)` and `programUserRoles(r, pid)` using `X-Komuna-User` or `userFromRequest(r)`; return `nil`/`[]` when unauthenticated or no membership row exists. Do **not** use `currentUser()` here because it falls back to the demo user and can leak demo membership/roles into anonymous/new-user responses.
- Make `programTree()` resolve ID, stored slug, and generated slug (`slugify(name)`) so any slug emitted by the list DTO can be fetched by detail routes.
- In `apps/web/src/lib/api.ts`, normal `ApiClient` requests should set `credentials: 'omit'`. Auth endpoints can still use `credentials: 'include'` when intentionally setting/clearing cookies, but public data fetches must not silently authenticate via stale cookies.
- Defensively gate membership UI by frontend auth state too: program cards should ignore `p.membershipStatus` unless `authClient.useSession()` has a real user, and `HeroSection`/CTA should ignore `membershipStatus`/`userRoles` when `isAuthenticated` is false. This prevents **Book/Leave/Rejoin** showing for guests even if bad/stale API data arrives.

**Regression checks:**
- Extend the signup workspace regression test to call `GET /api/v1/programs` with the new token and assert every `membershipStatus` is `null` before joining.
- Also fetch `GET /api/v1/programs/<id-or-slug>` with that token and assert `membershipStatus == null` and `len(userRoles) == 0`; this catches the detail-page “Rejoin program” bug.
- Add a route test that gets a slug from `GET /api/v1/programs`, then verifies `GET /api/v1/programs/<slug>` returns 200.
- Add a frontend `ApiClient` test asserting request init has `credentials: 'omit'`.
- Add a frontend program-detail regression where `authClient.useSession()` returns guest/null but the mocked program has `membershipStatus: 'active'` and roles; assert the page shows **Sign in to join** and not **Member**/**Leave Program**.
- Manual public probe: as a guest and as a fresh temporary user, fetch a detail endpoint and confirm `membershipStatus: null` and `userRoles: []`. Then join a public program and confirm detail returns `membershipStatus: active`. For UI regressions, also verify the deployed JS asset contains `credentials:\`omit\`` and the visible guest CTA is not **Book/Leave/Rejoin**.

### Guests Can Join Programs Instead of Being Sent to Login

**Symptom:** An anonymous visitor clicks **Join**, sees “You joined the program,” and is redirected to the program sessions/page instead of the login/signup page.

**Root cause:** `joinProgram()` used `currentUser(r)`. In Komuna, `currentUser()` intentionally falls back to the demo/dev user when no authenticated session exists. That is unsafe for mutating user actions: it can create `program_members` rows for the demo user and return success to guests.

**Fix pattern:**
- For mutating user-specific endpoints, authenticate explicitly with `X-Komuna-User` or `userFromRequest(r)`; do **not** call `currentUser()` unless demo fallback is intentionally allowed.
- Return `401 auth_required` when no real session exists. The frontend already routes `ApiError(401)` through `redirectToSignInForUnauthorized(...)`, so the smallest backend fix restores the UI redirect behavior.
- Keep `currentUser()` use limited to read/demo-compatible paths, or audit every caller before using it in new code.

**Regression check:** Add a test that posts to `/api/v1/programs/<id>/join` without auth, expects `401`, and verifies no membership was inserted for `app.userID`/demo user.

**Manual probes:**
```bash
curl -i -X POST http://127.0.0.1:8095/api/v1/programs/prog-box/join
curl -i -X POST https://komuna.ahsanworks.com/api/v1/programs/prog-box/join
# Both must return 401 {"error":"auth_required"}
```

### Superadmin Missing Dashboard Button

**Symptom:** A known superadmin logs in but the top-nav/profile Dashboard button is missing. They may only have member roles in programs.

**Root cause:** `apps/web/src/lib/useWorkspace.ts::canAccessDashboard()` grants access when `/api/v1/me/workspace` returns `isSuperAdmin: true`; the Go API sets that from `platform_admins` in `api/v1/main.go::workspace()`:

```go
a.db.QueryRow("SELECT COUNT(*) FROM platform_admins WHERE user_id=?", uid).Scan(&isSuperAdmin)
```

If `platform_admins` is empty or missing the user's exact `users.id`, `isSuperAdmin` is false and the frontend falls through to the admin/manager role check. A superadmin who is only a member will not see Dashboard.

**Check:**
```sql
SELECT id, user_id FROM platform_admins;
SELECT id, email, name FROM users WHERE email='USER_EMAIL';
SELECT id, email, name FROM auth_users WHERE email='USER_EMAIL';
```

**Fix:** Insert the user's `users.id` (which should match `auth_users.id`) into `platform_admins`; no service restart is needed because the handler reads the live DB.

```sql
INSERT INTO platform_admins(id, user_id)
VALUES ('pa-' || lower(hex(randomblob(4))), 'user-...');
```

**Verify:** Login, then call `/api/v1/me/workspace` with the session token/cookie and confirm `isSuperAdmin: true`. The dashboard button comes from `TopNav`/`ProfileMenu` using `canAccessDashboard(workspace)`.

**Seed pitfall:** Full reseed scripts must also seed `platform_admins`; otherwise reseeding silently removes all superadmins.

**Debugging pitfall — silent `currentUser` fallback to `user-demo`:** `currentUser()` (main.go:460) falls back to `a.userID` (env `KOMUNA_DEV_USER_ID`, default `user-demo`) when `userBySession` fails. This masks auth failures — the workspace endpoint returns HTTP 200 with `uid: user-demo` and `isSuperAdmin: false` instead of 401. If you see `uid: user-demo` in a workspace response for a real authenticated user, the session token lookup is failing (check `auth_sessions` table for the token, verify expiry format matches `time.RFC3339`).

### Admin/Manager CTA Changes Role in UI But Reverts After Refresh

**Symptom:** On the admin members dashboard, clicking Add/Remove admin or assigning manager products shows an optimistic UI update, but after refreshing the member is back to basic member / previous roles.

**Root cause:** The frontend calls `POST`/`DELETE /api/v1/programs/:programId/members/:userId/roles` from `apps/web/src/pages/MembersPage.tsx`. If `api/v1/program_handlers.go::programMembers` does not dispatch `action == "roles"`, the generic `len(parts) >= 4` branch can return `{"success":true}` without writing `program_member_roles`. This creates a silent success/no-op.

**Fix pattern:**
- In `programMembers`, dispatch `roles` before ban/unban success handling:
  ```go
  if action == "roles" {
      a.programMemberRole(w, r, pid, uid)
      return
  }
  ```
- Implement `programMemberRole` to decode `{ role, productId? }`, validate `admin|manager`, look up the member by `(program_id,user_id)`, and write/delete `program_member_roles`.
- For product-scoped manager roles, also keep `product_managers` in sync with `program_member_roles.product_id`; manager role without `product_id` will not show assigned products in workspace.
- For unscoped admin rows with nullable `product_id`, do not rely on `UNIQUE(program_member_id, role, product_id)` to dedupe NULLs in SQLite. Delete any existing `product_id IS NULL` row before inserting, or use a non-NULL sentinel/schema change deliberately.

**Regression check:** Add a Go test that posts `{"role":"admin"}` to `/api/v1/programs/prog-box/members/<userID>/roles`, asserts `program_member_roles` has the row, then fetches `/members` and checks `"role":"admin"` is returned. Also smoke a temporary live member and clean it up after verifying persisted count.

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

### Go `http.ServeMux` Route Conflict — Same Path, Different Methods

**Symptom:** Service panics on startup with `pattern "/api/v1/profile/picture" conflicts with pattern "/api/v1/profile/picture"` even though the two registrations use different HTTP methods (e.g., one POST, one DELETE).

**Root cause:** Go's `http.NewServeMux` (pre-1.22) registers handlers by **path**, not by method. Registering `HandleFunc("/api/v1/profile/picture", wrap("POST", fn1))` and `HandleFunc("/api/v1/profile/picture", wrap("DELETE", fn2))` both register the same path pattern → panic at `mux.HandleFunc`. The method check inside `wrap` happens too late — the mux panics during registration.

**Fix:** Use a single `"*"` method handler and dispatch by `r.Method` internally:
```go
// Route — single registration
h("/profile/picture", "*", a.profilePicture)

// Handler — dispatch internally
func (a *App) profilePicture(w http.ResponseWriter, r *http.Request) {
    if r.Method == "DELETE" {
        a.profilePictureDelete(w, r)
        return
    }
    if r.Method != "POST" {
        errOut(w, 405, "method_not_allowed")
        return
    }
    // POST logic...
}
```

This follows the same pattern already used by `sessionTree`, `notificationTree`, and `claimTree` — a single `"*"` handler that parses URL sub-paths and dispatches.

### SQLite ALTER TABLE Idempotency

**Symptom:** After a mid-migration crash (e.g., the route-conflict panic above), the ALTER TABLE already ran but the service panicked before starting. On restart, the ALTER TABLE fails with `SQL logic error: duplicate column name` and the service won't boot.

**Root cause:** SQLite doesn't support `IF NOT EXISTS` for `ALTER TABLE ADD COLUMN`. The schema execution loop in `NewApp()` treats every error as fatal.

**Fix:** Make the schema loop tolerate "duplicate column name" errors from ALTER TABLE:
```go
for _, q := range schema() {
    if _, err = db.Exec(q); err != nil {
        // Ignore "duplicate column name" errors from ALTER TABLE (idempotent schema)
        if strings.Contains(q, "ALTER TABLE") && strings.Contains(err.Error(), "duplicate column") {
            continue
        }
        return nil, fmt.Errorf("schema: %w (sql: %s)", err, q[:min(80, len(q))])
    }
}
```

This lets the service restart cleanly after a mid-migration crash without manual DB intervention.

### Go `rows.Scan` Silent Failure with SQLite NULL Columns

## Go nil slice → JSON `null` pitfall

When building a JSON response with a slice that may be empty:

```go
// BROKEN — nil slice marshals to null, crashes frontend .length/.map calls
var cards []any
for rows.Next() { cards = append(cards, ...) }
jsonOut(w, map[string]any{"items": cards, ...})
// → "items": null  (if zero rows matched)

// FIXED — empty slice marshals to [] 
cards := []any{}
for rows.Next() { cards = append(cards, ...) }
// → "items": []
```

**Symptoms:** Frontend blank page on filtered views with zero results (e.g., "ongoing" tab with no sessions). Console: `TypeError: Cannot read properties of null (reading 'length')`. React unmounts after uncaught render error.

**Affected handlers:** `programSessions` (line 236) and any handler that conditionally appends to a nil-initialized slice. Always initialize with `:= []any{}` or `:= make([]any, 0)`.

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

### Restricted Route Auth Guards — Demo User Fallback Leaks

**Symptom:** Opening restricted pages as a guest returns `200 OK` data, empty account pages, platform metrics, or dashboard payloads instead of redirecting to login / returning `401`.

**Root cause:** The Go API's `currentUser()` helper falls back to the configured demo/default user when no real session exists. Restricted handlers must not call it directly.

**Fix:** Use a strict `requireUser(w, r)` helper in restricted handlers and return `401 auth_required` when no bearer/cookie session exists. Add a table-driven unauthenticated regression test for workspace, wallet, purchases, bookings, notifications, profile preferences, platform dashboard, and program admin/member/manage routes. Wrap direct frontend routes (`/wallet`, `/my/bookings`, `/notifications`, `/settings/notifications`, `/profile`) with an auth guard so guests redirect to sign-in instead of seeing page-level errors.

See `references/restricted-route-auth-guards.md` for the compact pattern and route checklist.

### Frontend Route Auth Guards — "??" and "User" After Sign-Out

**Symptom:** After signing out, pressing back in browser loads a dashboard URL. Top bar shows `'??'` avatar and `'User'` name instead of real user info. User can still access dashboard pages.

**Root cause:** `WorkspaceRoute` (the component wrapping all `/programs/:id/admin`, `/programs/:id/manage`, `/programs/:id/member` routes) had no auth check. It rendered `DashboardShell` unconditionally, and `ProfileMenu` fell back to `getInitials(null) = '??'` and `displayName = 'User'` when `authClient.useSession()` returned `{data: null}` (localStorage cleared by sign-out).

**Fix:** Add `authClient.useSession()` check with `<Navigate to="/auth/sign-in" replace />` when session is null. Same pattern applies to any protected route.

**Affected files:** `apps/web/src/components/routing/WorkspaceRoute.tsx` (fixed). Several standalone pages (`/wallet`, `/profile`, `/my/bookings`, `/notifications`) also lack auth guards — they show error states instead of redirecting.

#### Backend Auth Fallback Leak (`currentUser()`)

**Symptom:** An unauthenticated browser can open restricted pages or call restricted APIs and receive `200 OK` data instead of being redirected/signaled as unauthenticated. Examples to audit: `/me/workspace`, `/wallet`, `/purchases`, `/my/bookings`, `/notifications`, `/notifications/unread-count`, `/notifications/preferences`, `/profile/preferences`, `/platform/dashboard`, `/programs/:id/member/dashboard`, and mutating actions such as `/programs/:id/join`.

**Root cause:** Handlers call `currentUser(r)`, which falls back to `a.userID/a.userEmail/a.userName` (demo/default user) when no bearer token or `komuna_session` cookie exists. That helper is unsafe for production restricted routes; it masks missing auth and can leak demo/default-user data.

**Audit pattern:** Probe unauthenticated with a browser-like user agent so Cloudflare does not block the diagnostic request before it reaches the app:
```bash
curl -sS -H 'Accept: application/json' -H 'User-Agent: Mozilla/5.0' \
  -i https://komuna.ahsanworks.com/api/v1/wallet
```
Expected for restricted routes is `401` (or `403` for role-only platform/admin routes), not `200` with empty/demo data. Also probe `http://127.0.0.1:8095/api/v1/...` to distinguish app behavior from Cloudflare.

**Fix pattern:** For restricted handlers, use `userFromRequest(r)` directly and return `errOut(w, 401, "auth_required")` when it fails. Only use `currentUser(r)` for intentional dev/demo fallback paths. For public list/detail DTOs, keep using explicit membership helpers that return `nil` when unauthenticated.

See `references/frontend-auth-guards.md` for the full auth architecture, route audit, and verification commands.

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
