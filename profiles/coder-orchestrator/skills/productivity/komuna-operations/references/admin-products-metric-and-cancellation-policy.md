# Admin products metric and cancellation policy planning note

Use this when planning or implementing Komuna Admin Dashboard **Products** tab changes involving the table `Sessions` column or voucher cancellation rules.

## Product table metric pitfall

The Products tab is a product setup/management surface. A column labeled only **Sessions** is ambiguous because it can be read as live generated sessions, while existing frontend code has used `product.sessionsPerWeek`. In the current Go API path, `productDTO` sets `sessionsPerWeek` from `a.productSessionCount(p.ID)`, and `productSessionCount` runs `SELECT COUNT(*) FROM sessions WHERE product_id=?`; this is a generated/live session row count, not the weekly template.

When the user asks what the number is getting pulled from, answer directly with the source first, then recommend the product-management metric change. Do not implement/deploy from that question alone unless the user explicitly asks to change it.

Preferred resolution for this surface:

- Rename the column to **Days / week** or **Available days** when the value comes from the weekly product template.
- Populate it from distinct weekdays in the product weekly availability/template slots.
- Keep simple products as `—`.
- Use **Active sessions** only if the user explicitly wants generated/live session instances duplicated on this page; if so, rename the column to **Active sessions** and back it with active non-cancelled session counts.
- Do not leave the label as just **Sessions** after changing the source.

Relevant files observed in the current Komuna app shape:

- Frontend table/form: `apps/web/src/pages/ProductsPage.tsx`
- Frontend tests: `apps/web/src/__tests__/ProductsPage.test.tsx`
- API DTO: `apps/api/src/dto/products.ts`
- Product controller list route: `apps/api/src/controllers/products.ts`
- Product service tier sorting: `apps/api/src/services/products.ts`

## Cancellation policy UI pitfall

The existing product cancellation tier storage can represent a three-band policy with no schema migration. Avoid arbitrary repeated tier rows if the product requirement is:

1. more than **X** hours before session → compensation voucher,
2. between **X** and **Y** hours → shorter-validity compensation,
3. less than **Y** hours → no compensation voucher.

Model the UI as fixed policy fields, then save only voucher-issuing tiers:

```ts
cancellationTiers: [
  { hoursBefore: earlyHours, validityValue: earlyValidityDays },
  { hoursBefore: lateHours, validityValue: lateValidityDays },
]
```

The final “less than Y” band is represented by no matching tier, not by adding a third no-voucher row. Validate `earlyHours > lateHours`, hours >= 1, and validity days >= 1.

Suggested defaults when no product-specific policy exists:

- early: more than 24 hours → 30-day compensation voucher,
- late: between 24 and 4 hours → 7-day compensation voucher,
- too late: less than 4 hours → no voucher.
