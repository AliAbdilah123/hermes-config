# Banned member action guards

Use when fixing Komuna bugs where a user with `program_members.status='banned'` can still perform member actions because an endpoint only checks for the existence of a membership row.

## Symptom

A banned user can still reserve/book a session or initiate checkout for a package, especially if they already have an active voucher/subscription.

## Root cause pattern

Handlers query membership like:

```sql
SELECT id FROM program_members WHERE program_id=? AND user_id=?
```

or voucher/subscription eligibility via joins to `program_members` without filtering `pm.status='active'`. That treats `banned`, `inactive`, and `left` as eligible members.

## Minimal fix shape

1. Resolve the target program at the backend write boundary:
   - claim booking: session -> product -> program
   - checkout: package -> program
2. Require active membership before side effects:

```go
func (a *App) isActiveProgramMember(uid, programID string) bool {
    var c int
    a.db.QueryRow(`SELECT COUNT(*) FROM program_members WHERE user_id=? AND program_id=? AND status='active'`, uid, programID).Scan(&c)
    return c > 0
}
```

3. Add `pm.status='active'` to voucher/subscription eligibility queries so stale benefits on banned memberships are not claimable.
4. Return `403` (for example `member_banned`) before inserting purchases, voucher claims, or incrementing session `taken`.

## Regression test

Add one test that creates:
- user
- banned `program_members` row for the program
- active voucher/subscription/package eligibility

Then assert:
- `POST /api/v1/claims` returns `403`
- `POST /api/v1/checkout` returns `403`
- no `voucher_claims` rows were created
- no `purchases` rows were created

Watch the test fail first: before the fix, claims can return `200` and create a claim despite banned status.

## Scope note

This guard blocks dangerous write actions. It does not decide whether banned users may view public program detail, sessions, products, or packages; keep UI visibility decisions separate unless the user explicitly requests them.