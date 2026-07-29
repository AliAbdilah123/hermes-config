# Platform superadmin grants (SQLite)

Use this for direct, production-like Komuna SQLite role grants.

## Safe procedure

1. Work from the Komuna project root and identify the active database by confirming it contains `platform_admins`, `auth_users`, and application data. Do not assume every `sqlite.db` found in subdirectories is active.
2. Inspect `platform_admins` schema before writing.
3. Resolve the target through `auth_users`, not `users`. Historical data may contain duplicate `users.email` rows, while `auth_users.email` is unique and identifies the actual login account.
4. Create a timestamped database backup before mutation.
5. Grant idempotently:

```sql
INSERT INTO platform_admins(id, user_id)
SELECT :admin_id, id
FROM auth_users
WHERE lower(email) = lower(:email)
ON CONFLICT(user_id) DO NOTHING;
```

6. Fail the operation if a verification query returns no row. Verify by joining `platform_admins.user_id` back to `auth_users.id` and matching the normalized email.
7. Run `PRAGMA integrity_check;` and require `ok` before reporting success.

## Pitfalls

- Do not select an arbitrary row from `users` by email: duplicate historical profile rows can grant admin rights to an ID that is not used for authentication.
- SQLite `RAISE()` only works inside trigger programs. For an ad-hoc grant, enforce “target found / grant present” in the calling shell or application after the idempotent statement.
- Do not report success merely because `sqlite3` exited cleanly: `INSERT ... SELECT` can affect zero rows when the email does not exist.
- Keep the backup path in operational output, but the user-facing response can remain concise unless they request details.
