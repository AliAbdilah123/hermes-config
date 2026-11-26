# Go + SQLite transaction verification

## Deadlock probe

When `database/sql` is configured with `SetMaxOpenConns(1)`, code inside an open transaction must not call a helper that queries through the parent `*sql.DB`. The transaction owns the only connection, so the helper waits forever for that same connection.

Keep authorization and dependent reads on the transaction:

```go
err := tx.QueryRow(`
  SELECT r.user_id, r.group_id
  FROM redemptions r
  JOIN memberships m ON m.group_id = r.group_id
  WHERE r.id = ? AND m.user_id = ? AND m.role = 'admin'
`, redemptionID, actorID).Scan(&userID, &groupID)
```

Alternatively, perform authorization before `Begin`, but only when the decision cannot become stale or the mutation rechecks it transactionally.

## Verification

- Run the state-transition test uncached with a finite timeout: `go test -count=1 -run TestName -timeout 30s ./...`.
- A timeout at a nested DB helper is evidence to inspect connection ownership, not merely increase the timeout.
- Exercise approve/reject or equivalent transactional branches independently; compile-only checks do not expose pool starvation.
- Then run formatting, the full test set, `go vet ./...`, and `go build`.
