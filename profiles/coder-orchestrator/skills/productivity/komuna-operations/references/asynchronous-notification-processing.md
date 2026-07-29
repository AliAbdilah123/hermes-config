# Asynchronous notification processing

Use this pattern for Komuna's current Go + SQLite deployment.

## Naming

- Product/UI/docs term: **asynchronous notification processing**.
- Internal implementation term: **SQLite-backed job queue**.
- Runtime component: **notification worker**.
- User-visible operational states: `pending`, `processing`, `delivered`, `failed`.

Do not unnecessarily expose “queue” as product language when “asynchronous processing” describes the behavior more clearly.

## Processing boundary

Keep these synchronous:

- Insert the in-app notification alongside the triggering business change.
- Read/unread mutations.
- Notification preference updates.
- Safe internal `action_url` navigation.

Process these asynchronously:

- Email, push, and SMS delivery.
- Session reminders and voucher-expiry generation.
- Provider/network retries and other slow external side effects.

## Minimal implementation

Reuse SQLite; do not add Redis for a single-instance deployment.

1. In one database transaction, persist the business change, insert the in-app notification, and enqueue any delivery job.
2. Store jobs with `queued | running | done | failed`, attempts, `run_at`, `locked_at`, and `last_error`.
3. Atomically claim the oldest eligible job. Start with one sequential worker.
4. On failure, retry with bounded backoff; mark permanently failed after the attempt limit.
5. On startup, recover jobs left `running` beyond the stale-lock threshold.
6. Make handlers idempotent. Deduplicate deliveries by `event_type + recipient_id + target_id + channel` (or an equivalent unique key).
7. Keep arbitrary payload editing out of admin UI; failed jobs may expose error details and a controlled Retry action.

## Verification

Cover at minimum:

- Business mutation and enqueue commit together.
- Concurrent workers cannot both claim one job.
- Failures reschedule and eventually become failed.
- Startup recovers stale running jobs.
- In-app notifications remain immediately visible.
- Duplicate webhooks/retries do not duplicate delivery.
- Disabled preferences suppress applicable processing.

## Preview rule

For Komuna preview work, implement in the existing isolated feature worktree when the user identifies one. Use an isolated preview database/API, exercise notification creation → worker processing → unread update → action navigation on the exact public preview URL, and leave production unchanged until explicit approval.
