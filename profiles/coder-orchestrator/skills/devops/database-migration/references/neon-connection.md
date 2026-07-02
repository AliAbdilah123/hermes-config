# Neon PostgreSQL Connection

This project uses Neon PostgreSQL with the connection pooler endpoint. The psycopg2 approach is most reliable.

## Connection details

- Host: `ep-bold-hall-a19pt070-pooler.ap-southeast-1.aws.neon.tech`
- Database: `neondb`
- User: `neondb_owner`
- SSL mode: `require`

## Connecting from Python

```python
import psycopg2

# Store password in pgpass file first
with open('/tmp/.pgpass_self') as f:
    host, port, db, user, pwd = f.read().strip().split(':')

conn = psycopg2.connect(
    host=host,
    port=port,
    dbname=db,
    user=user,
    password=pwd,
    sslmode='require'
)
```

## Known quirks

1. The `users` table has an FK constraint referencing `auth_users_ref` — insert into `auth_users_ref` before inserting users.
2. Drizzle ORM generates its own IDs via `gen_random_uuid()` — the `id` column defaults are in the DB, not app-side.
3. Enum columns use custom PG types (e.g., `"Goal status"`, `"Task status"`) — cast with `::text` when reading for migration.
4. The pooler endpoint rotates IPs (52.220.170.93, 13.228.46.236, 13.228.184.177) — each new psql connection may hit a different IP.
5. psql has intermittent auth failures with the pooler; psycopg2 is more reliable for multi-query operations.
