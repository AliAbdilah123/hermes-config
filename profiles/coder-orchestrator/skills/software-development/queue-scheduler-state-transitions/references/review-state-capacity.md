# Review-state capacity: concrete recipe

## Example policy table

| State | User meaning | Blocks next queued item? |
|---|---|---:|
| `todo` | Waiting to run | No |
| `in_progress` | Agent is executing | Yes |
| `in_review` | Agent output awaits human approval | No |
| `blocked` | Operator intervention required | Yes, when product policy freezes the lane |
| `done` | Complete | No |

The key distinction is that `in_review` is unfinished but idle. Human review should not leave execution capacity unused unless the product explicitly requires serial approval.

## Minimal SQL shape

When the scheduler already selects the first queued item and atomically changes it from queued to running, reclassifying review can be a one-token-set change:

```sql
NOT EXISTS (
  SELECT 1
  FROM jobs active
  WHERE active.lane_id = candidate.lane_id
    AND active.state IN ('in_progress', 'blocked')
)
```

Keep the atomic guarded claim, such as `UPDATE ... WHERE state='todo'`, unchanged.

## Deterministic regression recipe

1. Pause automatic scheduling during fixture creation.
2. Insert one predecessor in `in_review` at position 0.
3. Insert one `todo` item at position 1.
4. Point execution at an `httptest`/fake server whose response waits on a release channel.
5. Unpause and invoke one scheduling pass.
6. Assert the second item is `in_progress`, has attempt count 1, and has exactly one running execution row.
7. Release the fake server in deferred cleanup before closing the application.
8. Repeat or use table-driven cases for `in_progress` and `blocked`, asserting the second item remains queued and has no running execution row.

## Verification trap

A command such as `go test ./pkg -run WrongName` can exit 0 while printing `warning: no tests to run`. This is no evidence. Use the exact function name and require output containing `=== RUN TestName` and `--- PASS: TestName`.