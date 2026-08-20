# Historical-row trigger failures

## Signature

- Transition endpoint returns a generic 500 such as `transition_failed`.
- Destination-specific input is valid.
- Fresh test fixtures pass, but an older production row fails.
- A later migration added a trigger enforcing required active-row fields.

## Investigation

1. Read every trigger from `sqlite_master` for the transitioned table.
2. Follow the transaction statement by statement until the trigger fires.
3. Compare required fields on the failing row and a newly created row.
4. Locate the migration that created the trigger and determine whether pre-existing rows were backfilled.
5. Build an upgrade fixture at the old migration level, apply all current migrations, then run the same transition sequence.

## Minimal repair

Add a one-time migration scoped to historical active rows that already satisfy all other required-field predicates. Use existing timestamps in deterministic preference order:

```sql
UPDATE opportunities
SET required_due_at = COALESCE(
  NULLIF(TRIM(stage_entered_at), ''),
  NULLIF(TRIM(last_activity_at), ''),
  NULLIF(TRIM(updated_at), ''),
  created_at
)
WHERE archived_at IS NULL
  AND stage NOT IN ('Won', 'Lost')
  AND owner_id IS NOT NULL
  AND owner_id > 0
  AND TRIM(COALESCE(next_action, '')) <> ''
  AND TRIM(COALESCE(required_due_at, '')) = '';
```

Mirror the trigger's scope closely. Do not disable the trigger, weaken the invariant, or patch only one transition endpoint.

## Regression matrix

- Current fixture: perform the normal preceding transition, then the reported transition; both succeed.
- Historical fixture: create under the old schema, migrate, assert the repaired field, then execute the same transitions.
- Atomicity: on a genuinely invalid row, stage/history/events remain unchanged.
- Runtime: confirm the migration version and repaired field in the database used by the running process.
- Public browser: authenticate, select the destination through the real UI, submit confirmation, require a 2xx POST, verify success notice and persisted stage/version after reload.

## Production E2E identity

If the record belongs to another tenant, create a dedicated identity through public registration and grant only the minimum membership required for that tenant. Do not reset or reuse the reported user's password. Remove temporary scripts, cookie jars, and local artifacts after verification.