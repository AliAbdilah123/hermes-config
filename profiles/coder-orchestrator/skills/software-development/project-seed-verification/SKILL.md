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

Use this when the user asks whether a project/app has been seeded, has enough demo data, or whether the live app contains expected fixture data.

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

5. **Report in three buckets**
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
- If counts include `None`/missing arrays in JSON state, treat them as zero and keep probing rather than crashing the verification.

## References

- See `references/komuna-seed-verification.md` for a concrete example where rich legacy seed scripts existed, but the deployed SQLite API contained only baseline demo data.
