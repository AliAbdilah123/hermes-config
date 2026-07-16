# Admin products metric and cancellation policy planning note

Use this when planning or implementing Komuna Admin Dashboard **Products** tab changes involving the table `Sessions` column or voucher cancellation rules.

## Product table metric pitfall

## Product table metric pitfall

The Products tab is a product setup/management surface. A column labeled only **Sessions** is ambiguous because it can be read as live generated sessions, while existing frontend code has used `product.sessionsPerWeek`.

Preferred resolution for this surface:

- Rename the column to **Days / week** when showing the weekly template count; the user approved the display format **`3 days / week`**.
- Populate the value from distinct weekdays in `session_templates.weekly_slots`, not from generated `sessions` rows.
- In the current Go API shape, `productDTO` still exposes the compatibility field `sessionsPerWeek`; update the backing helper rather than introducing a new API field unless a broader API cleanup is requested.
- Keep simple products as `—` in the admin table even if the API compatibility field is `0`.
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

The final “less than Y” band is represented by no matching tier, not by adding a third no-voucher row. In `ProductsPage.tsx`, normalize old stored tiers by filtering out `validity_value`/`validityValue` values of `0` or `null`, sorting remaining voucher tiers descending by hours, and filling missing values from defaults. Validate `earlyHours > lateHours`, hours >= 1, and validity days >= 1.

Suggested defaults when no product-specific policy exists:

- early: more than 24 hours → 30-day compensation voucher,
- late: between 24 and 4 hours → 7-day compensation voucher,
- too late: less than 4 hours → no voucher.

## i18n follow-through pitfall

When changing visible Products tab copy, do not hardcode the new English labels in `ProductsPage.tsx`. Add/update both `apps/web/src/i18n/en.json` and `apps/web/src/i18n/id.json`, and render through `t(...)` so the Indonesian language toggle remains complete. This applies to compact values like `{{count}} days / week` as well as form policy text such as the cancellation bands and no-voucher fallback.

Verification markers after deploy:

- Public JS bundle contains the English marker (for example `Days / week`).
- Public JS bundle also contains the Indonesian marker (for example `Hari / minggu` or `tidak ada voucher kompensasi`).
