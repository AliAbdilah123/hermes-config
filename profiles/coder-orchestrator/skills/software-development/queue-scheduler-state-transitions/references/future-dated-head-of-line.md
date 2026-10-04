# Future-dated head-of-line jobs

Use when a positional FIFO lane allows a queued item to become eligible only at a future timestamp and later items must wait behind it.

## Minimal model

Persist one nullable due timestamp on the queued item. Do not add a lifecycle state merely to represent time eligibility:

- `NULL` or due timestamp: eligible under normal queue rules;
- future timestamp: remains queued but is not claimable;
- later rows in the same lane: must not bypass the future-dated head;
- other lanes: remain independently schedulable.

Normalize accepted timestamps to one UTC representation before persistence. If SQLite compares timestamp text directly, use a single sortable format and pin the behavior with a test.

## Predicate placement

Preserve FIFO by separating head selection from due-time eligibility:

```sql
WHERE j.state = 'todo'
  AND j.id = (
    SELECT q.id FROM jobs q
    WHERE q.lane_id = j.lane_id AND q.state = 'todo'
    ORDER BY q.position LIMIT 1
  )
  AND (j.scheduled_at IS NULL OR j.scheduled_at <= CURRENT_TIMESTAMP)
```

The due condition belongs on the outer, already-selected head. Putting it inside the head subquery filters out the future job and incorrectly lets the next row leapfrog it.

## Deterministic regression contract

1. Create a future-dated head and an unscheduled follower in one lane.
2. Run one scheduling pass.
3. Assert both remain queued, neither attempt count increments, and neither has a run record.
4. Make the head due and run one pass.
5. Assert only the head is claimed: running state, incremented attempt, one running execution record.
6. Add a due item in another lane and prove it can start while the first lane waits.
7. Preserve tests for active-running and policy-blocking states.

## Migration and API checks

- Add the nullable column to both fresh schema and idempotent upgrade path.
- Preserve it in every table-rebuild migration; upgrades can otherwise silently discard it.
- Validate at the API boundary, normalize to UTC, and treat omission as immediate eligibility.
- Cover JSON and multipart creation paths when both exist; malformed timestamps must create no row.
- Convert browser-local `datetime-local` values to absolute timestamps before submission, while storing the local control value in drafts.
- Return the schedule through every list/detail DTO used to render queued items.

## Deployed behavioral verification

When safe test accounts and fixtures are supported, verify through the authenticated public API rather than treating process health as E2E:

1. Create a future-dated head and an immediate follower in the same lane through public endpoints.
2. Wait beyond one scheduler tick and fetch both through the public API; assert both remain queued and the head exposes its schedule.
3. Make the head due through a supported mutation. If the product intentionally has no schedule-edit API, a controlled database update is acceptable only on an isolated test fixture and must be identified as test setup.
4. Wait one tick, then assert the head has a real claim side effect (attempt increment/run record or corresponding public detail) while the follower remains queued.
5. Clean up both fixtures even when assertions fail.

Authenticated HTTP verification proves backend queue behavior, not rendered controls, accessibility, or browser-console cleanliness. Keep browser E2E as a separate gate and report that boundary explicitly if unavailable.
