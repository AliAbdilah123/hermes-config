# Session/product/package image tone fallback

Use when Komuna cards show the browser broken-image icon, blank image area, or inconsistent placeholder for products, packages, or session instances.

## Durable pattern

- Session instances do **not** own images in v1; `GET /programs/:id/sessions` derives `SessionCard.imageUrl` from the joined product row (`products.imageUrl`). If session cards break, first verify the API still maps `row.productImageUrl ?? ''` into `imageUrl` before changing frontend behavior.
- Frontend cards must handle both absent URLs and broken URLs:
  - render the real `<img>` only when `imageUrl && !imageFailed`
  - set `onError={() => setImageFailed(true)}`
  - render the site's existing image-tone placeholder when missing/broken
- Apply the fallback at every card component that renders the entity class, not only the reported page. For Komuna session instances this includes:
  - `apps/web/src/pages/all-sessions/SessionCard.tsx`
  - `apps/web/src/pages/all-sessions/SessionCardCompact.tsx`
  - product/package card analogues when relevant

## Minimal test shape

Use Testing Library to simulate the browser image failure:

```tsx
fireEvent.error(screen.getByAltText('Jab Class'))
expect(screen.queryByAltText('Jab Class')).not.toBeInTheDocument()
expect(screen.getAllByText('Jab Class').length).toBeGreaterThan(1)
```

This catches regressions where a broken URL leaves the browser's broken-image icon instead of the tone fallback.

## Verification

- `cd apps/web && npm run test -- SessionCardCompact.test.tsx`
- `cd apps/web && npm run build`
- Deploy built `dist/` to the live nginx path and verify the public bundle changed.
