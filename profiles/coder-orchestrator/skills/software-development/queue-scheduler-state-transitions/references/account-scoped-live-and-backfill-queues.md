# Account-scoped live and backfill queues

Use when historical recovery/backfill and live events can target the same account.

## Durable model

- Scope lease/lock by connected account identity, not globally or by provider. Accounts on the same provider must remain independent.
- Put live and historical items in the same durable queue before processing; uniqueness should include provider + external event/message ID.
- Historical items drain by provider timestamp with a stable ID tie-breaker.
- If live arrivals must preempt history, persist an explicit priority/class and order by priority first. Timestamp-only ordering does not implement preemption.
- Delete only after the canonical processor succeeds or confirms a duplicate.
- On the first failure, retain the row with attempt/error metadata and stop. Retry that barrier before later historical work.
- Use expiring leases. If work can outlive the lease, renew it; if expiry allows another owner to claim, release with an owner token rather than deleting a lock by account alone.

## Integration boundary

Queue routing should return whether it handled the event. For social inboxes, only active matched identities enter the account queue; unmatched/pending verification events must fall back to the existing onboarding processor so activation and verification replies are preserved.

For provider history, resolve the account/sender conversation first, then fetch that conversation's messages. Bound pagination and report whether the known local boundary was reached; successful pagination is not proof that retention exposed all missed history.

## Tests

- Same account excludes a second drainer; different accounts proceed concurrently.
- Historical FIFO and deterministic ties.
- Duplicate is harmless.
- Failure remains first and blocks advancement.
- Live event under occupied lease is durably queued; when preemption is required, it runs before remaining history.
- Pending verification still follows onboarding.
- Crash/expiry recovery cannot let an old worker release a new owner's lease.

Availability checks are not behavioral proof. A public 200 and unauthenticated 401 verify deployment/routing/auth only; claim full E2E only after an authenticated account sync and observed queue/domain result.