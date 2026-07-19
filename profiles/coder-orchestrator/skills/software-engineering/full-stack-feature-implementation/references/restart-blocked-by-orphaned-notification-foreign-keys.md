# Restart blocked by orphaned notification foreign keys

Use when a deployment build succeeds but the service restart fails because startup runs `PRAGMA foreign_key_check` and reports notification rows whose referenced jobs/job-runs no longer exist.

## Safe recovery

1. Read `systemctl status` and recent journal output; do not report the deployment live merely because `systemctl restart` returned before the crash loop became visible.
2. Stop the service before changing SQLite data.
3. Back up the database and its SQLite sidecars if present.
4. Run `PRAGMA foreign_key_check;` and verify the failures are limited to orphaned notification references.
5. Delete only notification rows proven orphaned with `NOT EXISTS` predicates against each nullable parent reference. Do not disable foreign keys or broadly delete notification history.
6. Re-run `PRAGMA foreign_key_check;`; it must return no rows.
7. Start the service, wait for actual HTTP readiness, then verify the new index asset hashes and feature-specific bundle markers through both localhost and the public URL.

Example predicate shape:

```sql
DELETE FROM notifications
WHERE (job_id IS NOT NULL AND NOT EXISTS (
  SELECT 1 FROM jobs WHERE jobs.id = notifications.job_id
)) OR (job_run_id IS NOT NULL AND NOT EXISTS (
  SELECT 1 FROM job_runs WHERE job_runs.id = notifications.job_run_id
));
```

## Prevention

Archive/delete flows that remove jobs or job runs must also remove, null, or preserve their dependent notifications according to the schema policy. Add a focused regression test so normal archive operations cannot create rows that make the next restart fail.
