# Hardcoded analytics placeholders left in production

Use this when an admin/analytics dashboard shows suspicious fixed percentages or zero/empty breakdowns despite live purchases, vouchers, or attendance rows existing.

## Detection

- Search the API handler for literal metric responses before tracing frontend rendering: `attendance_rate`, `voucher_utilization`, `compensation_rate`, `no_show_rate`, `package_attribution`, `revenue`.
- Probe the deployed endpoint directly with auth headers/cookies and compare against database-backed facts:
  - paid purchases joined through program members for revenue
  - voucher status/source for utilization and compensation rates
  - voucher claims attendance status for attendance/no-show
  - purchase items joined to purchase packages for package attribution
- Watch for frontend code that multiplies ratios by 100. If the API contract expects `0.82`, returning `82` displays `8200%`.

## Minimal fix shape

- Replace literal response maps with scoped aggregate SQL queries filtered by program id.
- Keep the API response contract stable: numeric rates should be ratios in `[0,1]`; money remains the existing money string format.
- Use `COALESCE(SUM(...), 0)` or nullable scans for aggregates that may have no rows.
- Qualify columns (`v.status`, `v.source`) in joined aggregate queries to avoid silent scan failures from ambiguous-column SQL errors.
- Add a regression test that inserts one paid purchase, purchase item, claimed voucher, compensation voucher, present claim, and absent claim, then asserts the endpoint returns non-placeholder computed values.

## Deployment pitfall

After rebuilding a Go binary used by systemd, verify the running process is actually the new artifact:

```bash
sudo readlink -f /proc/<pid>/exe
strings /path/to/binary | grep 'unique query literal'
```

If the process exe shows `/path/to/server (deleted)`, an orphaned old process is still bound to the port and `systemctl restart` may fail with `bind: address already in use`. Stop the unit, kill the orphaned PID, `systemctl reset-failed`, start the unit, and verify `/health` plus the targeted public endpoint.