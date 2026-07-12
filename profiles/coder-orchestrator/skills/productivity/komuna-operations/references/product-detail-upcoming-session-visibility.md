# Product detail upcoming session visibility

## Trigger

Use when inactive session instances appear on a public program/product detail page even though the Admin Sessions dashboard shows them inactive.

## Root cause pattern

Product detail session previews are populated through:

- `apps/api/src/services/products.ts` → `ProductService.getProductDetail()`
- `options.sessionsService.listUpcomingSessions(productId)`
- `apps/api/src/services/sessions.ts` → repository `listUpcoming(productId)`

If `listUpcoming` only filters by `product_id` and `start_time >= now`, inactive generated template instances (`is_active = false`) still appear publicly. DTO mapping can then default scheduled lifecycle rows to user-facing `status: "open"`.

## Minimal fix

In `createDrizzleSessionRepository().listUpcoming(productId)`, require:

```ts
eq(sessions.productId, productId),
eq(sessions.status, 'scheduled'),
eq(sessions.isActive, true),
gte(sessions.startTime, new Date()),
```

Keep this backend-side; do not hide these rows only in the frontend.

## Verification

- Add/keep a targeted service regression around `SessionService.listUpcomingSessions` so repository filtering remains the visibility boundary.
- Run targeted API test:

```bash
cd /home/ubuntu/projects/komuna/apps/api
npm run test -- src/services/__tests__/sessions.test.ts
```

- Query live/local DB shape for affected product:

```sql
SELECT id, product_id, start_time, status, is_active, template_id
FROM sessions
WHERE product_id = '<product-id>'
ORDER BY start_time;
```

Inactive future template rows should not be returned by the product-detail upcoming-sessions path.
