# Komuna seed verification example

This reference captures a reusable pattern from checking whether a migrated project had been seeded with necessary data.

## Situation

The repository contained rich legacy seed files under an older stack:

- `apps/api/src/db/seed.ts`
- `apps/api/src/db/seed-kaltim.ts`

Those files seeded many users, programs, products, packages, sessions, vouchers, claims, audit logs, and notifications, including a large Kaltim coworking/workspace dataset.

However, the active deployed stack was a Go + SQLite API in `api/v1/main.go`, not the old Neon/Drizzle app. The active API seeded state via an in-code `seed() State` function and stored it in SQLite table `app_state` as JSON.

## Verification pattern used

1. Locate seed files and read enough to understand expected dataset scope.
2. Check public health endpoint:
   - `GET /projects/komuna/api/v1/health` returned OK.
3. Check public programs endpoint:
   - `GET /projects/komuna/api/v1/programs?limit=3` returned two programs.
4. Inspect active SQLite database, decode `app_state.payload`, and count arrays.
5. Compare active runtime counts against richer legacy seed script claims.

## Observed active runtime counts

- Programs: 2
- Products: 3
- Packages: 2
- Sessions: 3
- Members: 1
- Vouchers: 2
- Claims: 1
- Requests: 2
- Purchases: 0 / missing array
- Audit logs: 1
- Notifications: 1
- Auth users: 4

Observed programs:

- `prog-box` — Jakarta Fight Club — Kemang, Jakarta
- `prog-yoga` — Bali Sunrise Yoga — Canggu, Bali

## Reporting lesson

The correct verdict was not simply "yes, seeded" or "no, not seeded." It was:

> Seeded enough for basic demo/testing flows, but not with the full rich production-like dataset available in legacy seed files.

Use this distinction for future project seed checks: **baseline/demo seeded** vs. **full necessary domain dataset seeded**.

## Auth users NOT seeded — empty workspace after sign-up pitfall

The Go API seed (`seed()` function in `api/v1/main.go`) creates application state (programs, products, members, sessions, vouchers, etc.) but **zero auth user accounts**. The `auth_users` table starts empty.

### How the dev user fallback creates confusion

```go
// main.go — currentUser fallback when no auth session exists
func (a *App) currentUser(r *http.Request) (string, string, string) {
    if u, ok := a.userFromRequest(r); ok { return u.ID, u.Email, u.Name }
    return a.userID, a.userEmail, a.userName  // ← dev user fallback
}
```

The dev user defaults to `user-demo` / `komuna@contact.aristoavilla.me` / `Demo User` (from `.env`). The seed creates one member (`pm-demo`) with `UserID: "user-demo"`, assigned as admin in `prog-box`.

**Result**: A visitor with no auth session appears to be "logged in" as Demo User and sees Jakarta Fight Club in their workspace. This gives the illusion of pre-existing accounts.

### What users actually need to do

1. **Sign up** (not sign in) at `/auth/sign-up` with any email + 8+ char password
2. After sign-up, workspace is **empty** — no programs joined
3. Browse programs and click **Join** on each program card
4. The password `KomunaSeed2026!` (or any other) is NOT a system password — it's whatever the user chooses at sign-up

### Debugging pattern

When a user reports "can't join as different users" or expects pre-existing login credentials:

1. Check `auth_users` table — if empty, confirm no seed accounts exist
2. Check `auth_sessions` for valid tokens — test with full 64-char hex token against `/api/v1/auth/session`
3. If `/me/workspace` returns `user-demo` despite a Bearer token, the token is likely wrong/truncated (64 hex chars needed) or the session expired
4. Public API curl test: `curl -X POST '<base>/api/v1/auth/sign-up' -H 'Content-Type: application/json' -d '{"email":"test@example.com","password":"Test1234!","name":"Test"}'` — should return token + user

### Truncated token pitfall

The Go API's `randomHex(32)` generates 64-character hex tokens. When inspecting the DB, token output may be truncated by display tools. A truncated token passed to `Authorization: Bearer` will fail session lookup silently, causing the API to fall back to `user-demo`. Always test with the exact full token from the database.

## Go `INSERT OR IGNORE` seed staleness pitfall

### The pattern

The Komuna Go API at `api/v1/main.go` uses this startup pattern:

```go
// Line 137 — runs on every startup
db.Exec("INSERT OR IGNORE INTO app_state(id,payload,updated_at) VALUES(1,?,?)", mustJSON(seed()), now())

// Line 232 — loads state from DB
a.db.QueryRow("SELECT payload FROM app_state WHERE id=1").Scan(&p)
```

`INSERT OR IGNORE` is idempotent: the first server launch seeds the DB. Subsequent launches load the serialized state from the DB — the `seed()` function is only called to produce the JSON that gets inserted. If the ID=1 row already exists, the insert is silently skipped and the **stale** previous seed data is loaded.

### Consequence

When you add a new struct field (e.g., `Featured bool`) and update the `seed()` function's data to include it, **the change will not take effect** if `sqlite.db` already exists. The binary is new but the DB contains the old serialized state without the new field (Go zero-values the missing field to `false`/`0`/`""`).

### Symptoms

- Binary built from source with `Featured: true` in seed data, but API returns `featured: false` for all records.
- `strings` on the binary confirms the field name exists but the struct literal values are compiled in — the issue is the DB, not the binary.
- Deleting the DB and restarting immediately fixes it.

### Debugging path that uncovered this

1. Checked source: seed data had `Featured: true` ✓
2. Rebuilt binary, verified same MD5 — still returned `featured: false`
3. Cleaned Go module cache, rebuilt — still `featured: false`
4. Compared binary checksums — identical, ruling out a build issue
5. Checked if SQLite DB existed and inspected `app_state` payload — found stale state without the new field
6. Deleted `sqlite.db` → re-seeded correctly → 6 featured programs returned

### Cure

```bash
sudo systemctl stop komuna-api
sudo rm -f /home/ubuntu/projects/komuna/sqlite.db
sudo systemctl start komuna-api
# Verify
curl -s "http://127.0.0.1:8095/api/v1/programs?featured=true"
```

### When to apply

Always delete the DB when:
- Changing the `seed()` function's data (not just the schema)
- Adding new struct fields that should have non-zero defaults in seed data
- Restructuring seed programs/products/packages counts

Do NOT delete the DB for:
- Pure code/logic changes (handler changes, DTO changes, auth flow changes)
- Situations where production auth users/sessions exist in the DB (back up first)
