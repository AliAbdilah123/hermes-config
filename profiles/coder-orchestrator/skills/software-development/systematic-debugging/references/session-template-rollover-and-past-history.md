# Session template rollover and past activated history

Use when an admin/manager scheduling UI shows a fixed number of upcoming recurring/template sessions, but an already-ended same-day slot remains visible or still shows an activation CTA.

## Symptom pattern

- The UI says “next N sessions shown”.
- Today’s earlier session remains in the list after its `end_time` has passed.
- The next recurring/template occurrence does not appear at the bottom to keep N future rows visible.
- A stale draft row still exposes `Activate`, but activation fails or is nonsensical for an ended time window.
- User asks for a “past activated sessions”/history tab.

## Root-cause checklist

1. Separate **date expansion** from **time-aware state**.
   - A helper that starts from today’s midnight/date can still generate sessions that are already ended today.
   - Filter by `end_time > now`, not just `date >= today` or `start_time >= today`.
2. Apply the same future-only filter to both persisted sessions and generated preview/template rows.
   - Common bug: saved rows are filtered with `!isEnded(s)`, but generated preview rows are pushed without an end-time check.
3. Keep generating until the visible quota is filled.
   - After dropping an ended row, continue template expansion so the next occurrence appears at the bottom.
4. Add a defensive activation guard.
   - The upcoming list should not contain ended rows, but `prepareActivate()`/CTA rendering should still reject `end_time <= now` to prevent stale UI or clock-race calls.
5. For history, prefer an existing active-session listing with computed `status=past` before adding new schema.
   - If the API computes `endTime <= now => past` and already filters `isActive = true`, it can serve a read-only “past activated sessions” tab.
6. Verify activation payloads separately.
   - If the frontend posts `{ managerId }` during activation, confirm the API actually validates/uses that body. A selected-manager issue can be masked by the past-slot activation failure.

## Minimal regression shape

- Freeze time just after the session ends, e.g. `now = 2026-07-13T18:01:00Z` for a `17:00–18:00` slot.
- Generate the next-N list from weekly slots.
- Assert the ended same-day slot is absent.
- Assert the next later template occurrence is present to keep N rows.
- Assert ended inactive sessions do not render an enabled activation action.
- Assert the history tab fetches/renders past active sessions newest-first and exposes no destructive actions.

## Komuna-shaped implementation notes

- `nextTemplateSessions()`-style helpers should accept `now = new Date()` for deterministic tests.
- Use a small helper such as:

```ts
function hasNotEnded(session: Pick<SessionItem, 'end_time'>, now = new Date()) {
  return new Date(session.end_time).getTime() > now.getTime()
}
```

- Past activated history can usually start as read-only and frontend-first via an endpoint shaped like `/programs/:id/sessions?status=past&sort=startTime_desc`, provided it returns active sessions with computed past status.
