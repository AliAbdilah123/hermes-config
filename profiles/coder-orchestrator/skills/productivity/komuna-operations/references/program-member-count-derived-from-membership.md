# Program discovery member counts must be derived from memberships

## Trigger

Use when the public/search programs page shows implausibly large member totals, or the screenshot/API returns counts like seeded marketing aggregates while the real member rows do not match.

## Root cause pattern

Komuna has had two API implementations:

- Cloudflare/Drizzle API under `apps/api/src/...` already derives `memberCount` from active `program_members` rows.
- The live Go+SQLite API under `api/v1/` may still be serving production. In that path, `programs()` and `programTree()` previously selected `programs.member_count`, a seeded/static column, and passed it into `programDTO`.

So searching only the React UI or the Drizzle service can falsely suggest the count is already dynamic while production is still hardcoded in the Go API.

## Minimal fix

In `api/v1/program_handlers.go`, replace `member_count` in both program list and detail SELECTs with a correlated count:

```sql
(SELECT COUNT(*)
 FROM program_members pm
 WHERE pm.program_id = programs.id
   AND pm.status = 'active')
```

Keep `rating`, `sessions_per_week`, and other display metadata unchanged unless the user asks for those too.

## Verification

1. Run Go tests from the legacy API directory:
   ```bash
   cd /home/ubuntu/projects/komuna/api/v1 && go test ./...
   ```
2. Rebuild/deploy the binary used by `komuna-api.service`.
3. Compare public API counts to SQLite directly:
   ```bash
   curl -s 'https://komuna.ahsanworks.com/api/v1/programs?limit=100'
   sqlite3 /home/ubuntu/projects/komuna/sqlite.db \
     "select p.id,p.name,count(pm.id) from programs p left join program_members pm on pm.program_id=p.id and pm.status='active' group by p.id,p.name order by p.name;"
   ```
4. Commit and push the fix.
