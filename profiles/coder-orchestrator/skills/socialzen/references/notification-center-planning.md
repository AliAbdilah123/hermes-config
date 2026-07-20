# Notification Center Planning

Use this reference when planning or implementing a persistent SocialZen notification center spanning publishing, analytics, account/security, and subscription events.

## Smallest durable architecture

- Add one user-scoped SQLite `notifications` table rather than a generic event bus.
- Store an immutable event snapshot in `details_json` so history remains readable if the related post/account/subscription later changes.
- Include `dedupe_key`, category, type, priority, title, summary, related entity identity, allowlisted deep link, read/archive timestamps, and created/updated timestamps.
- Enforce `UNIQUE(user_id, dedupe_key)` and index active history plus unread lookup.
- Use cursor pagination on `(created_at, id)`; offset pagination drifts when new rows arrive.
- Start with 30-second polling while the authenticated page is visible, plus refresh on focus. Add SSE/WebSockets only if measured latency/load requires it.
- Prefer an accessible Load More control over invisible infinite scroll for V1.

## Product behavior

- Shared `Topbar` owns the bell so every dashboard route gets it without per-page edits.
- Clicking a notification marks it read and opens its dedicated detail route first. The detail page then exposes the related action/deep link; this preserves complete historical context.
- `View All` opens Settings → Notifications.
- Delete is permanent. Archive hides from the active list but remains queryable through an archived filter.
- Group client-side using the user's timezone: Today, Yesterday, This Week, Older.
- Render icon, color, timestamp, category, read state, and priority; never encode priority/read state by color alone.

## Producer boundaries

Create notifications only after the source mutation commits:

- **Publishing:** after target and parent post status updates. Snapshot post ID, caption/title, platform, publish time, provider post/permalink, normalized error code/message/action, and retryability. Dedupe per post target and result transition.
- **Analytics:** after exact `post_target_metrics` persistence. Evaluate milestones by exact target/platform, not shared parent-post aggregate. Dedupe by target + metric + threshold.
- **Accounts:** after connect/disconnect or token-state transitions, not on every status read. Token-expiry warnings dedupe by account + expiry timestamp + warning window.
- **Security:** after email verification/password mutation succeeds.
- **Subscriptions:** after webhook/state transition succeeds; use provider event IDs or transition keys for dedupe.

Suggested initial analytics thresholds: views/reach 1k, 10k, 100k; likes/comments/shares/saves 100, 1k, 10k; engagement rate 5%, 10%, 20%; follower milestones only where account analytics actually exposes the source metric.

## API and routing

Provide authenticated, user-scoped endpoints for list/filter/search/cursor pagination, unread count, detail, mark read, mark all read, archive/unarchive, and delete. Validate enums, limits, cursors, JSON, ownership, and deep-link allowlists server-side.

Recommended frontend routes:

- `/app/settings/notifications`
- `/app/settings/notifications/:notificationId`

Register the detail route before broad Settings section routes so it cannot be swallowed by `settings/:section`. Internal links use React Router. External provider links require `https:` and `rel="noopener noreferrer"`.

## SocialZen-specific pitfalls

- Add schema changes to both `internal/models.Migrate()` and the legacy/test `app.migrate()` path.
- Production uses SQLite with `SetMaxOpenConns(1)`: materialize and close `Rows` before notification inserts or enrichment queries.
- Publishing retries and analytics refreshes can repeat. Producers must be idempotent through stable dedupe keys, not best-effort frontend suppression.
- Cross-platform analytics identity lives at `post_target_id`; parent post metric aggregation can create false milestones.
- Missing/deleted related records must not erase history. Show the stored snapshot and disable unavailable actions gracefully.
- Preserve unrelated dirty working-tree changes; stage notification files/hunks explicitly.

## TDD verification shape

1. Migration/repository tests: constraints, dedupe, user isolation, cursor ordering, filters/search, mutations.
2. Handler tests: authentication, ownership, validation, pagination metadata, unread count, 404s.
3. Producer tests: committed-boundary insertion, retry idempotency, exact snapshots, milestone crossing only once.
4. Frontend tests: badge cap, dropdown keyboard/Escape/outside click, polling reconciliation, timezone grouping, filters, Load More, detail actions/deep links.
5. Run full Go tests/build, Vitest, typecheck, and Vite build; deploy and verify the public JS content type before reporting completion.
