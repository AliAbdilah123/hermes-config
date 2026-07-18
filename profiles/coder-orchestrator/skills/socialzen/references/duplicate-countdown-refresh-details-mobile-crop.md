# Duplicate countdown, refresh details, and mobile crop layout

Use this reference when duplicated posts lose their countdown, analytics refresh only shows aggregate partial-success counts, or the photo cropper clips the image on mobile.

## Duplicate countdown

### Root cause pattern

The duplicate UI may send a selected `publishAt`, while the backend duplicate route drops the request object/body and inserts a hardcoded future timestamp. A countdown eligibility check such as:

```ts
post.status === "SCHEDULED" && publishAt - updatedAt < 5 * 60 * 1000
```

then correctly hides the countdown because the persisted duplicate is many hours away.

### Fix

- Pass the HTTP request into the duplicate handler.
- Decode and validate `publishAt` as RFC3339 and require a future time.
- Persist that exact normalized UTC timestamp.
- Capture one `now` value for `created_at` and `updated_at` so countdown eligibility is deterministic.
- Do not widen the countdown threshold to mask bad persistence.

Regression checks: valid requested time is preserved; missing/malformed/past time returns `400`.

## Analytics partial-success details

### Root cause pattern

The backend already returns target-level `results` (`postTargetId`, `platform`, `status`, `message`), but the frontend type narrows each item to `{status}` and formats only aggregate counts. The data exists but is discarded at the API/UI boundary.

### Fix

- Expand the frontend response type to retain target identity, platform, status, and message.
- Keep the aggregate summary first.
- Append one line per result so successes, partials, and failures are all identifiable.
- Render the existing status container with `whitespace-pre-line` (or a semantic list) so detail lines remain readable.
- Keep the backend unchanged when it already provides the required detail.

Regression check: formatter output includes the summary plus successful, partial, and failed target IDs/messages.

## Mobile photo crop controls

### Root cause pattern

A fixed desktop grid (`minmax(0,1fr) 260px`) inside a clipped modal makes the image column overflow on narrow screens. Global `body.style.touchAction = "none"` also prevents reaching controls after they are stacked below the image.

### Minimal responsive fix

- Add stable classes to the modal, grid, and menu while preserving desktop inline styles.
- Under a phone breakpoint, override the grid to one column; DOM order naturally moves the right menu below the preview.
- Remove global/backdrop touch suppression; retain `touch-action: none` only on the crop interaction surface/handles.
- Make the modal vertically scrollable and reduce canvas-panel padding on mobile.
- Use `!important` only where responsive CSS must override React inline styles.

Example CSS:

```css
@media (max-width: 700px) {
  .photo-crop-modal { overflow-y: auto !important; }
  .photo-crop-layout {
    grid-template-columns: minmax(0, 1fr) !important;
    min-height: 0 !important;
  }
  .photo-crop-canvas-panel { padding: 12px !important; }
  .photo-crop-menu {
    border-left: 0 !important;
    border-top: 1px solid var(--line);
    overflow: visible !important;
  }
}
```

Regression checks: responsive classes/media rule exist, body touch suppression is absent, crop-surface touch handling remains scoped, typecheck/build pass, and deployed CSS/JS markers are present.

## Delivery

When the user explicitly says to skip planning, implement directly after a compact root-cause inspection. Run focused RED/GREEN tests, full relevant tests, typecheck/build, deploy both changed tiers, verify public asset content types/markers, then commit and push.