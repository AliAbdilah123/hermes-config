# Purchase-status dashboard aggregate audit

Use when a user suspects a Komuna admin overview total includes pending purchases.

## Verification sequence

1. Identify the exact UI metric and endpoint feeding it; do not infer behavior from labels such as “total purchases” or “revenue.”
2. Trace the backend aggregate to its SQL/status predicate. Revenue and completed-purchase counts should use an explicit `status = 'paid'` filter when pending payments are not realized revenue.
3. Query SQLite grouped by both program and status, applying the same date boundary as the UI:

```sql
SELECT p.name, pu.status, COUNT(*) AS purchases,
       SUM(CAST(pu.total_amount AS REAL)) AS amount
FROM purchases pu
JOIN program_members pm ON pm.id = pu.program_member_id
JOIN programs p ON p.id = pm.program_id
GROUP BY p.id, pu.status;
```

4. Compare the displayed value with paid-only and paid-plus-pending candidate totals.
5. Report paid and pending counts/amounts separately, then state whether pending contributes to the displayed metric.

## Pitfalls

- The purchases list may intentionally include every status while overview revenue excludes pending; these are separate contracts.
- Global totals can hide a program-scoped error. Match the dashboard’s program and date scope.
- Matching current data alone is insufficient; verify the code predicate so the conclusion survives data changes.
- Keep investigation read-only unless the user explicitly asks to implement a fix.
