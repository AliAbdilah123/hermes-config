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

**NEVER delete `sqlite.db` to re-seed.** This wipes all auth_users, auth_sessions, members, vouchers, claims, purchases, and any runtime data. Instead, always **merge data into the live database** using Python/SQLite.

The database has two layers:
1. **`app_state` table** — a single-row JSON payload containing programs, members, vouchers, claims, sessions, packages, products, requests, audit log, notifications, and settings. This is the entire application state.
2. **`auth_users` and `auth_sessions` tables** — separate tables for authentication.

### Safe Pattern: Read-Modify-Write app_state via Python

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

### Adding Seed Programs Without Damage

1. Read current programs from live DB via `curl http://127.0.0.1:8095/api/v1/programs`
2. Identify which programs need adding (check by ID)
3. Use the Python read-modify-write pattern above to insert only missing programs
4. Restart service
5. Verify via `curl http://127.0.0.1:8095/api/v1/programs | python3 -c "import json,sys; print(len(json.load(sys.stdin)['data']))"`

### WAL Checkpointing

When the Go service is running, SQLite WAL mode means recent writes live in `sqlite.db-wal`, not the main file. Always run `PRAGMA wal_checkpoint(TRUNCATE)` before reading from Python to get the full current state.

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
├── api/v1/main.go       # Go API — single-file, ~1700 lines
├── api/server           # Compiled binary
├── api/v1/main_test.go  # Tests
├── sqlite.db            # Live database (DO NOT DELETE)
├── apps/api/            # Cloudflare Worker (TypeScript, separate deployment)
├── apps/web/            # React SPA (Vite)
└── docs/                # Project documentation
```

### Linked Files

- `scripts/hash_password.py` — standalone script to hash a password matching Go API's algorithm. Run directly: `python3 scripts/hash_password.py somepassword`

## Full-State Reseeding (Complete DB Replacement)

When the user provides a full spec (users + programs + memberships + roles), write a Python script that builds the entire `app_state` payload and populates `auth_users`. The script must produce JSON that Go's `json.Unmarshal` can deserialize into the `State` struct.

### JSON Type Pitfalls (Go → Python)

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

## Verification Checklist

- [ ] `go test ./...` passes before deploying
- [ ] `go build -o ../server .` succeeds
- [ ] `sudo systemctl restart komuna-api.service` completes
- [ ] Internal health: `curl -sS http://127.0.0.1:8095/api/v1/health`
- [ ] Public programs: `curl -sS https://komuna.ahsanworks.com/api/v1/programs`
- [ ] Login test: sample user via `POST /api/v1/auth/sign-in`
- [ ] Workspace test: `GET /api/v1/me/workspace` with Bearer token for role verification
- [ ] Git committed and pushed after meaningful changes
- [ ] Database was NOT deleted — only modified via Python/SQLite if needed
