# Supabase PostgreSQL → project SQLite notes

Use when copying a Supabase-hosted Postgres DB into a local project SQLite DB with a small API compatibility schema.

## Supabase connection fallback

Some Supabase direct DB hosts resolve only to IPv6 in this environment, producing `Network is unreachable` even with the correct password. Use the pooler instead:

```python
psycopg2.connect(
    host='aws-0-us-east-1.pooler.supabase.com',  # region must match project
    port=6543,
    dbname='postgres',
    user='postgres.<project_ref>',
    password='<db_password>',
    sslmode='require',
)
```

If region is unknown, probe likely pooler hosts and stop at the first successful `select current_database(), current_user`. `ENOTFOUND tenant/user` means wrong region/project ref for that pooler, not necessarily bad password.

## Mapping pattern from Supabase app tables to SQLite API tables

Typical Supabase tables may be:

- `profiles(user_id uuid, email, created_at)` → SQLite `users(id,email,password_hash,metadata,created_at)`
  - Use `user_id::text` as `users.id`.
  - If password hashes are unavailable from Supabase auth, insert a placeholder such as `supabase-migrated-login-disabled`; users may need password reset or re-auth flow after migration.
- `wallets.shared_with uuid[]` → SQLite JSON text `shared_with` via `json.dumps(shared_with or [])`.
- PostgreSQL `uuid`, `bigint` IDs → SQLite `TEXT` IDs with `str(id)` when the target schema uses text PKs.
- PostgreSQL booleans → SQLite `0/1` integers.
- PostgreSQL `date/timestamptz` → ISO text.
- If source table lacks `updated_at`, duplicate `created_at` into the SQLite `updated_at` field rather than inventing current time.

## Required-field filtering

SQLite schemas often enforce fields that Supabase source rows allowed to be NULL. Before insert, count and skip/repair rows that violate target NOT NULL constraints, e.g. transactions with NULL `date`, `amount`, `type`, or `wallet_id`; categories with NULL `wallet_id`.

## Verification

After migration:

```bash
sqlite3 sqlite.db "PRAGMA foreign_key_check; PRAGMA integrity_check;"
sqlite3 sqlite.db "SELECT 'users',count(*) FROM users UNION ALL SELECT 'wallets',count(*) FROM wallets UNION ALL SELECT 'transactions',count(*) FROM transactions;"
curl -fsS http://localhost:<port>/api/health
```

Remove any temporary migration/probe scripts that contain credentials before finishing.