# Product detail can show inactive upcoming sessions

## Symptom

On a public program/product detail page, users see upcoming session cards even though the admin sessions table shows those session instances as inactive.

Concrete observed case: Balikpapan Coastal Yoga Studio → Sunrise Vinyasa showed three Tuesday sessions on 2026-07-14, 2026-07-21, and 2026-07-28. Live DB rows had `status='scheduled'` and `is_active=0`.

## Root cause pattern

The product detail endpoint builds `upcoming_sessions` via `ProductService.getProductDetail()`:

```ts
upcomingSessions = await options.sessionsService.listUpcomingSessions(productId)
```

That delegates to `SessionRepository.listUpcoming(productId)`, which historically filtered only by:

```ts
eq(sessions.productId, productId)
gte(sessions.startTime, new Date())
```

It did **not** filter `sessions.isActive = true`. The DTO mapping then used `mapSessionListItemToDTO(session)` without computed status extras, so a lifecycle `scheduled` row defaults to public `status: 'open'` even when `is_active` is false.

## Triage checklist

1. Confirm product/program IDs:
   ```sql
   SELECT id, name, slug FROM programs WHERE name LIKE '%Balikpapan%' OR slug LIKE '%balikpapan%';
   SELECT p.id, p.program_id, p.name, p.slug, p.type
   FROM products p JOIN programs pr ON pr.id=p.program_id
   WHERE pr.name LIKE '%Balikpapan%' OR p.name LIKE '%Sunrise Vinyasa%';
   ```
2. Confirm suspicious sessions:
   ```sql
   SELECT id, product_id, start_time, end_time, status, is_active, template_id
   FROM sessions
   WHERE product_id='<product-id>'
     AND start_time >= '<month-start>' AND start_time < '<next-month-start>'
   ORDER BY start_time;
   ```
3. Inspect the API path before editing UI. If `upcoming_sessions` comes from product detail, the bug is likely backend filtering, not a card rendering issue.

## Fix direction

For public/product-detail upcoming sessions, filter to active upcoming rows, typically:

```ts
and(
  eq(sessions.productId, productId),
  eq(sessions.isActive, true),
  eq(sessions.status, 'scheduled'),
  gte(sessions.startTime, new Date()),
)
```

Keep admin session lists separate: admins may need to see inactive/scheduled rows for management. Add a regression around `getProductDetail()` or repository `listUpcoming()` proving inactive future rows are excluded from `upcoming_sessions` while active future rows remain.
