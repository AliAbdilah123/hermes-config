# Go SQL Query Construction Debugging

## When to Use

A SQL query works fine in `sqlite3`/`psql` CLI but fails when executed via a Go API handler — particularly `"SQL logic error: near '<token>': syntax error"`.

## Pattern: Dynamic WHERE Clause with Conditional Parentheses

Common in Go backends that build `WHERE` clauses with string concatenation and conditional branches. The bug pattern:

```go
where := "where user_id=?"
if includeMain {
    where += " and (category='Main' or (1=1"  // opens TWO parens
}
// ... date filters ...
where += ")"  // closes only ONE paren → unbalanced!
```

**Root cause**: When `includeMain=true`, the `(category='Main' or (1=1` opens two parentheses but only one `)` is appended at the end.

**Fix**: Close with the right number of parens:

```go
if includeMain {
    where += "))"  // close both
} else {
    where += ")"   // close one
}
```

## Diagnosis Workflow

1. **Test the raw SQL** against the DB CLI with the exact query string and args. If it works there, the issue is in Go string construction.
2. **Trace every branch** in the WHERE-clause builder. Count opens vs closes per conditional path.
3. **Use Python for HTTP testing** instead of curl when tokens are involved — shell escaping can silently corrupt long tokens (UUID concatenations, special chars):

```python
import urllib.request, json
req = urllib.request.Request('http://localhost:8096/api/endpoint?params')
req.add_header('Authorization', f'Bearer {token}')
resp = urllib.request.urlopen(req)
```

## Verification

After fix: rebuild, restart, test the exact API endpoint with the same params that triggered the error. Verify the data shape matches expectations (correct row count, correct fields).

## Pitfall: Concurrent API During Data Migrations

When an in-process API is running while data ownership is changed (e.g., bulk `UPDATE user_id`), the API can create **duplicate records** under the new owner. Example: `ensureDailyGoalForDate` creates a new empty daily goal because the existing goal still belongs to the old user at that moment. After the migration, both goals belong to the same user — and the frontend may pick the empty one.

**Prevention**: Stop the API service before running ownership-transfer SQL, then restart.
