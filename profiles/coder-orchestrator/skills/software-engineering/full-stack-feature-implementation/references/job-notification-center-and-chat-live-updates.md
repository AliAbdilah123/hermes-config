# Job Notification Center and Chat Live Updates

Use this pattern when an agent/job application already has job events, a job-detail modal, and per-job streaming, but needs chat presentation plus board-wide completion/error notifications.

## Minimal architecture

1. **Reuse job events for chat rendering**
   - Keep the existing event API and persistence.
   - Map user-authored event kinds such as `comment` or `input` to right-aligned bubbles.
   - Map provider `output` and `error` events to left-aligned bubbles.
   - Preserve whitespace with `white-space: pre-wrap`; do not duplicate conversation storage.

2. **Separate detail streaming from global status awareness**
   - Existing per-job SSE updates only an open detail modal; it cannot notify a user watching the board about another job.
   - Prefer an authenticated user-level SSE stream for global completion/error events.
   - A short polling interval is an acceptable fallback when adding a broadcast stream is disproportionate. Poll both notifications and board state so cards visibly leave `in_progress` without reopening the page.
   - Avoid showing old notifications as fresh toasts: establish the initial ID set first, then toast only IDs first observed on later refreshes.

3. **Persist notifications idempotently**
   - Store `user_id`, nullable `job_id`, `job_run_id`, terminal `kind`, title/message, read state, and creation time.
   - Add a uniqueness constraint such as `(job_run_id, kind)` so repeated reconciliation or terminal callbacks cannot duplicate notifications.
   - Create the notification beside the successful terminal state transition, not in the browser.
   - Scope every list/update query by authenticated user.

4. **Use cursor pagination**
   - Initial request returns the latest 10.
   - Fetch older pages with `before=<last-id>` ordered by descending ID.
   - Return `has_more` and unread count.
   - Deduplicate appended pages by notification ID.
   - Trigger the next page near the scroll container's bottom; a visible manual load control can remain as an accessibility fallback if needed.

5. **Reuse one job-detail modal authority**
   - Notification and toast clicks should mark the row read, fetch the referenced job detail if needed, and set the same existing `selectedJob`/`job` state used by board-card clicks.
   - Do not create a second modal or notification-specific job-detail route.
   - Decrement unread state only when the clicked notification was previously unread.

6. **Honor the requested bulk action literally**
   - `Mark unread` means setting the user's currently loaded/all notifications unread; do not silently reinterpret it as “mark all read.”

## TDD checks

Backend:
- latest-10 pagination and `has_more`
- owner isolation for list and mutation
- read/unread transition
- one notification per run/outcome despite duplicate terminal callbacks
- completion and error creation paths

Frontend:
- event-kind-to-bubble-side mapping
- page merge deduplication
- initial fetch does not toast historical rows
- later completion/error produces a toast
- toast and menu item use the existing job-detail modal state

## Active-root integration pitfall

A feature can compile, pass helper tests, and appear in the production bundle while still being absent from the UI if it was wired into an obsolete component (for example, `LegacyApp`) rather than the component passed to `createRoot(...).render(...)`.

Before declaring frontend delivery:
- Trace the actual render root and component call chain from `createRoot` to the visible header/page.
- Search for duplicate or legacy app shells before choosing an insertion point.
- Add a component-level regression check that renders the active shell or a shared exported notification-center component and asserts the accessible bell is present even when the notification list is empty.
- Treat bundle-string presence as build evidence only, not proof that the active DOM renders the feature.
- After deployment, verify the authenticated DOM or a screenshot contains the bell beside the account avatar and that clicking it opens the menu.

## Verification

- Run frontend tests and production build.
- Run the complete backend test suite and build the embedded/static frontend in the correct order.
- Restart the service and verify the public index references the new asset hashes.
- Verify a distinctive notification/chat marker in the public bundle **and** the authenticated active DOM; bundle markers alone do not prove reachability.
- Create or transition a safe test job where possible and confirm card state, persistent notification, toast, read transition, and modal opening.
