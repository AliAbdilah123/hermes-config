---
name: database-migration
description: Cross-engine database copy/migration between SQLite and PostgreSQL (Neon). Schema mapping, column renaming, type conversion, junction table flattening, and connection troubleshooting. Use when copying DB content between different engines or ORM schemas.
triggers:
  - Copy/migrate database between SQLite and PostgreSQL
  - Move data from Neon Postgres to local SQLite (or vice versa)
  - Cross-ORM schema mapping (Drizzle → Go sql, or similar)
  - DB connection string has password that needs env-var or pgpass workaround
---

# Database Migration: SQLite ↔ PostgreSQL

Cross-engine database copy/migration with schema mapping between different ORM backends.

## Step 1: Clarify direction

**ALWAYS confirm source → target before writing any code.** Ask the user explicitly if the direction is ambiguous. A wrong-direction copy wastes time and may dirty the target.

## Step 2: Inspect both schemas

Before writing migration code, inspect BOTH sides:

```bash
# SQLite
sqlite3 <path> ".schema"
sqlite3 <path> "SELECT COUNT(*) FROM <table>"  # for each table

# PostgreSQL (use psycopg2 with pgpass file — see connection notes below)
python3 -c "
import psycopg2
# query information_schema.columns for each table
"
```

## Step 3: Identify schema differences

Common mismatches when migrating between Drizzle/Node.js and Go/sql:

| Concern | Drizzle (PG) | Go (SQLite) |
|---------|-------------|-------------|
| IDs | `uuid` with `gen_random_uuid()` | `text` (string UUIDs) |
| Column case | camelCase (`isTemplate`, `templateId`) | snake_case (`is_template`, `template_id`) |
| Junction tables | Separate table (`task_goals`) | Direct FK column (`tasks.goal_id`) |
| Boolean | `boolean` | `integer` (0/1) |
| Dates | `date` / `timestamptz` | `text` (ISO strings) |
| Enums | Custom PG enum types | `text` with CHECK constraints |
| FK constraints | May have auth ref tables (`auth_users_ref`) | Direct FK references |

## Step 4: Write the migration script

Always **backup first**: `shutil.copy2(db_path, db_path.with_suffix('.db.bak-<date>'))`

### PG → SQLite pattern

```python
import sqlite3, psycopg2
from pathlib import Path
import shutil

# Backup
DB = Path('/path/to/sqlite.db')
shutil.copy2(DB, DB.with_suffix('.db.bak'))

# Connect to PG (see connection notes)
# Connect to SQLite (PRAGMA foreign_keys = OFF for bulk insert)

# 1. Handle missing FK parents: if PG users table is empty but content
#    references user IDs, create placeholder users
sc.execute("SELECT DISTINCT user_id FROM ...")  # collect all referenced IDs
for uid in distinct_ids:
    sc.execute("INSERT INTO users (...) VALUES (?, ...)", (uid, ...))

# 2. Map junction tables to direct columns
#    e.g., task_goals(task_id, goal_id) → tasks.goal_id
#    Use DISTINCT ON to pick first goal per task
pc.execute("SELECT DISTINCT ON (task_id) task_id, goal_id FROM task_goals ORDER BY task_id, created_at")
task_goal = dict(pc.fetchall())

# 3. Convert types in-flight
#    bool → int:  1 if pg_val else 0
#    uuid → text: pg_val  (psycopg2 returns Python UUID, cast with ::text)
#    enum → text: pg_val::text

# 4. Insert in FK-safe order
#    users → goals → task_groups → tasks → energy_readings → habits → habit_options → habit_logs → focus_plan → focus_item
```

### SQLite → PG pattern

```python
# 1. auth_users_ref must exist before users (FK constraint)
cur.execute("INSERT INTO auth_users_ref (id) VALUES (%s) ON CONFLICT DO NOTHING", (pg_id,))
cur.execute("INSERT INTO users (...) VALUES (...)", (...))

# 2. Map direct columns → junction tables
#    tasks.goal_id → INSERT INTO task_goals (task_id, goal_id)
# 3. int → bool:  bool(sqlite_val)
# 4. text → uuid:  pg val is just the string (PostgreSQL accepts text for uuid columns)
```

## Step 5: Verify

```bash
sqlite3 <path> "PRAGMA integrity_check;"
# For each table: SELECT COUNT(*) and compare
```

If the app is running, hit its health endpoint to confirm no breakage.

## PostgreSQL connection (Neon)

Neon connections can be tricky. Preferred approach:

```bash
# Store password in pgpass file
echo "host:5432:dbname:user:password" > /tmp/.pgpass && chmod 600 /tmp/.pgpass

# Then use psycopg2 in Python
with open('/tmp/.pgpass') as f:
    host, port, db, user, pwd = f.read().strip().split(':')
conn = psycopg2.connect(host=host, port=port, dbname=db, user=user, password=pwd, sslmode='require')
```

**Pitfall**: The terminal tool masks database passwords as `***` in output, but this masking is display-only for user-shared connection strings. When you later construct commands with `PGPASSWORD='...'`, the password you type is sent literally — password masking in output does NOT mean you can use `***` as the password.

**Pitfall**: Neon's `users` table may have an FK to `auth_users_ref` — insert into `auth_users_ref` first.

**Pitfall**: Neon pooler endpoint (`-pooler`) can have connection flakiness. If psql fails with auth errors on some commands but not others, switch to psycopg2 which reconnects reliably.

## Support files

- `references/neon-connection.md` — Neon PostgreSQL connection quirks and setup
- `references/pg-to-sqlite-mapping.md` — Session-specific schema mapping notes (Drizzle → Go API)
- `references/drizzle-pg-to-go-sqlite-relational.md` — Komuna full 25-table migration: Drizzle/Postgres → Go/SQLite with type mapping, pitfalls, and seed patterns
- `templates/pg_to_sqlite_migrate.py` — Reusable migration script template

## Pitfalls

- **Wrong direction**: Always confirm source→target. Starting the wrong way dirties the target.
- **Schema column name mismatch**: Check BOTH schemas before writing mapping code. Drizzle's camelCase vs Go's snake_case is a common surprise.
- **Missing FK parents**: If the source has referenced IDs with no parent rows, create placeholder parents rather than dropping the data.
- **Bool ↔ int conversion**: SQLite stores bools as 0/1 integers, PG uses proper boolean. Convert explicitly.
- **No rollback on SQLite**: Back up before running migration scripts. Keep the backup until verified.
- **Live API during data fixes creates duplicates**: When an API server is running and you run bulk data-modification SQL (ownership transfers, ID rewrites), the API can create duplicate/temporary records under the new owner mid-migration because its queries see the old state. Stop the API service first, run the SQL, then restart. This applies to any in-place data fix, not just cross-engine migrations.
- **Go sql.Scan NULL into string**: SQLite NULL columns cannot be scanned into Go `string` — it panics with "converting NULL to string is unsupported". Fix: use `COALESCE(col,'')` in the query, or scan into `sql.NullString`. Applies to all nullable TEXT columns (image_url, description, location, slug, reason, etc.).
- **Go sql.Scan INTEGER into bool**: SQLite stores booleans as INTEGER (0/1). Scanning directly into Go `bool` fails on some drivers (modernc.org/sqlite). Scan into `int` and convert with `val != 0`.
- **SetMaxOpenConns(1) deadlock in Go+SQLite**: With a single connection, nested queries deadlock — if `rows.Next()` holds the connection and the loop body calls `db.Query()`, the inner query blocks forever waiting for the connection the outer query holds. Fix: set `SetMaxOpenConns(10)` or close rows before inner queries. WAL mode makes concurrent reads safe.
