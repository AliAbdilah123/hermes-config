# Serial-column board controls

Use when extending a Kanban-like board where Columns are execution lanes rather than workflow-status groups.

## Domain semantics

- A Column is a serial/FIFO execution queue: at most one Job runs in that Column at a time.
- Separate Columns are independent and may execute concurrently.
- Job status is card state, not Column identity. Do not move/regroup Jobs when status changes.
- A board-level **Add job** targets the tail of the final Column.
- Preserve per-Column **Add job** controls for explicit placement.
- Preserve a distinct trailing **Add column** tile after the last Column; it must also remain available on an empty Board.

## Empty-board Add job

1. On activation, synchronously acquire a lock (`useRef` or equivalent), not only async UI state. React state alone can allow two rapid clicks before rerender.
2. If no Columns exist, POST through the ordinary Column-creation path with ordinary defaults (for example a blank name that invokes the server's random-name generator). Do not invent a semantic name such as `Jobs` or `Todo`.
3. Await the created Column ID before opening the Job dialog.
4. On failure, keep the dialog closed, show an accessible error, release the lock, and send no Job request.
5. On success, open the existing Job form for that Column. If the user cancels, the empty Column may remain; avoid destructive rollback.

## API/UI integration

- Prefer existing `POST /boards/{board}/columns` and `POST /columns/{column}/jobs` routes; no schema change is normally required.
- If the board response does not include Jobs, enrich the Column listing with its ordered Jobs. With single-connection SQLite, collect/close Column rows before querying Jobs.
- Scope both Column and embedded Job reads through the authenticated user's Board ownership.
- Render Job detail from refreshed API/SSE state, using the card prop only as initial fallback; otherwise state-dependent actions remain stale.
- Keep the trailing Add-column tile inside the horizontal scroller. On mobile it remains after the final Column.

## Design-review checklist

A static Board proposal must visibly include all persistent creation controls, not only the newly requested one:

- top Board-level **Add job**;
- per-Column **Add job**;
- trailing **Add column**;
- empty-Board state showing both top Add-job and trailing Add-column controls;
- queue order/one-running-job semantics, without status-column visual language.

## Verification

- Existing Columns A/B/C: Board Add-job targets C and appends at C's tail.
- Empty Board: exactly one ordinary Column is created before the Job dialog opens.
- Rapid repeated activation cannot create duplicate Columns.
- A running Job is not interrupted; queued Jobs wait for predecessors to terminate.
- Other Columns can execute concurrently.
- Column creation failure opens no Job dialog and sends no Job POST.
- Job detail updates state/actions after API or SSE refresh.
- Both Add-job controls and the trailing Add-column control are keyboard accessible and visible at narrow widths.
