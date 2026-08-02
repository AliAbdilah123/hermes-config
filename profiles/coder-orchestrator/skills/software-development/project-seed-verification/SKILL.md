---
name: project-seed-verification
description: Verify whether a project has been seeded with necessary data by checking code-defined seed sources, active runtime storage, and public/API-visible data.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [seed-data, database, smoke-test, verification, sqlite, api]
---

# Project Seed Verification

Use this when the user asks whether a project/app has been seeded, has enough demo data, whether the live app contains expected fixture data, or asks for a database-backed testing account.

## Core principle

Do not answer from the presence of seed files alone. Verify the **active runtime data source** and, when available, the **public/API-visible behavior**. A project can contain rich seed scripts that are not the data currently served by the deployed app.

## Workflow

1. **Identify the project and runtime stack**
   - Locate project path from the conversation, channel memory, or obvious project directories.
   - Read project instructions if present (`AGENTS.md`, `README`, deployment docs) for the active runtime layout.
   - Determine whether the current deployment uses SQL tables, SQLite JSON state, a worker DB, etc.

2. **Find seed sources**
   - Search for seed files and migration backfills (`*seed*`, `fixtures`, `demo`, `INSERT INTO`, `seed()` functions).
   - Note what the seed source claims to create: programs/tenants, users, packages, products, sessions, vouchers, audit logs, notifications, etc.
   - Distinguish old/legacy seed scripts from the currently deployed stack.

3. **Find the active runtime data source**
   - Inspect env files without printing secrets; only report key names or sanitized state.
   - Check app startup code for DB path resolution and default locations.
   - For SQLite-backed apps, inspect the live DB file and its schema/size.
   - For JSON-in-SQLite state patterns, query/decode the state payload rather than assuming normalized tables exist.

4. **Verify externally visible data**
   - Hit public health/read endpoints where available.
   - Query representative public collection endpoints (programs/packages/sessions) and compare to DB counts.
   - If auth is required, use existing safe seed/demo credentials only if documented; do not invent credentials.

5. **For requested testing accounts, create through the real registration path when possible**
   - First identify the active service port, DB path, and request contract from runtime configuration and current handlers; do not assume common ports or JSON field names.
   - Prefer the public/API registration route because it creates related tenant, membership, and other required records transactionally.
   - If registration is unavailable and direct insertion is necessary, generate the password hash with the application's own algorithm/library, insert every required relational record in one transaction, and preserve ownership/permissions of the live DB.
   - Never store or reveal plaintext passwords from existing users. Generate a new dedicated testing credential instead.
   - Verify both the DB row/relationships and a real login against the active runtime. An integrity check or successful `INSERT` alone is insufficient.

6. **Report in three buckets**
   - **Verified seeded data:** counts and sample records actually observed in the active runtime/public API.
   - **Available but inactive seed data:** seed scripts or legacy fixtures in the repo that are not reflected in the active runtime.
   - **Verdict:** seeded enough for baseline/demo testing, or missing necessary production-like/domain-specific data.

## Verification snippets

### SQLite JSON app_state count probe

```bash
python3 - <<'PY'
import sqlite3, json, os
p = 'sqlite.db'
print('db_exists', os.path.exists(p), 'bytes', os.path.getsize(p) if os.path.exists(p) else None)
con = sqlite3.connect(p)
print('tables', con.execute("select name from sqlite_master where type='table' order by name").fetchall())
row = con.execute('select payload from app_state where id=1').fetchone()
if row:
    state = json.loads(row[0])
    for key in ['Programs','Products','Packages','Sessions','Members','Vouchers','Claims','Requests','Purchases','Audit','Notifications']:
        v = state.get(key)
        print(f'{key}: {len(v) if isinstance(v, list) else 0} ({type(v).__name__})')
PY
```

### Public API sanity check

```bash
curl -fsS "$PUBLIC_BASE/api/v1/health"
curl -fsS "$PUBLIC_BASE/api/v1/programs?limit=3" | head -c 2000
```

## Pitfalls

- `node_modules` may be missing even when the deployed app is healthy. Do not turn that into a tool limitation; use public endpoints or direct DB inspection instead.
- A seed file in an old app directory can be misleading after migrations. Confirm which app code currently serves production.
- Report sanitized env/config findings only; never print connection strings or secrets.
- Do not infer the active API from `localhost:8080`; inspect the service listener/runtime environment first. Multiple applications often coexist on one host, and a plausible response from the wrong service is a dangerous false signal.
- Go's JSON decoder matches struct field names case-insensitively, but it does not translate unrelated keys (for example, a handler expecting `Email`/`Username` will ignore a `login` key). Read the handler or frontend request payload before testing auth.
- If direct SQLite writes fail under the operator account, check file/directory ownership. Use the service account or narrowly elevated SQLite command rather than changing DB permissions; then verify the running process sees the row.
- If counts include `None`/missing arrays in JSON state, treat them as zero and keep probing rather than crashing the verification.
- **Go+SQLite `INSERT OR IGNORE` seed staleness**: When a Go API seeds state via `INSERT OR IGNORE INTO app_state` (idempotent first-run seed), subsequent code changes to the `seed()` function's data (new struct fields, changed values) will NOT take effect if the SQLite DB file already exists. The API loads the stale serialized state from DB on restart. Cure: stop the service, delete the SQLite DB file, then restart to trigger a fresh seed. Always verify with an API call after restart — don't just check the binary.
- **Seed app data ≠ seed auth users**: Some Go+SQLite APIs (e.g. Komuna) seed program/product/member state but zero auth user accounts. Combined with a dev-user fallback when unauthenticated, this creates the illusion of pre-existing login credentials. Users must sign up fresh, and after sign-up their workspace is empty (no programs joined). See `references/komuna-seed-verification.md` § "Auth users NOT seeded" for the full debugging pattern.

## References

- See `references/komuna-seed-verification.md` for a concrete example where rich legacy seed scripts existed, but the deployed SQLite API contained only baseline demo data.
- See `references/sqlite-copy-reseed-and-runtime-switch.md` when replacing an active SQLite dataset safely: backup API with WAL awareness, schema-equality and relationship gates, stopped-service sidecar archival, atomic promotion, and authenticated public role E2E.
