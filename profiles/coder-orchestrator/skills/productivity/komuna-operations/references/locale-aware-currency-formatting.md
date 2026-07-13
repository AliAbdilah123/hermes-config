# Locale-aware currency formatting in Komuna

## Trigger

Use this when a Komuna page shows money as a raw USD amount such as `$7,410,000` even though persisted purchase/package amounts are stored in IDR, or when language toggling should change both the amount and currency symbol.

## Root pattern

Komuna stores prices and purchase totals in IDR. Frontend display should route through the shared pricing formatter instead of ad-hoc `toLocaleString('en-US', { currency: 'USD' })` calls.

- Indonesian (`id`) should show IDR/Rupiah formatting, e.g. `Rp 7.410.000`.
- English (`en`) should convert IDR to USD using `VITE_USD_TO_IDR_RATE`, e.g. `7410000 / 16000 = $463.13`.
- Do not pass an explicit `currency: 'USD'` unless the value is already USD; explicit currency disables the stored-IDR conversion path.

## Fix checklist

1. Search frontend code for hardcoded currency formatting:
   - `toLocaleString('en-US'`
   - `currency: 'USD'`
   - custom helpers such as `formatCurrencyAmount`
2. For stored IDR values, delegate to `formatPriceLabel(String(value), locale ? { locale } : undefined)`.
3. If the component already has `useTranslation`, pass `i18n.language`; otherwise rely on the pricing helper's current-language lookup.
4. Add/extend a regression test with a large IDR amount so the old bug is obvious:
   - `formatCurrencyAmount(7410000, 'id')` contains `Rp` and `7.410.000`
   - with `VITE_USD_TO_IDR_RATE=16000`, `formatCurrencyAmount(7410000, 'en') === '$463.13'`
5. Run the targeted pricing/purchase tests and `npm run build`, then deploy the web `dist/` to the Komuna nginx path and verify the public bundle hash.

## Pitfalls

- A helper that always returns USD can make IDR totals look like millions of dollars.
- Existing `formatPriceLabel` conversion only applies when no explicit currency override is provided.
- Purchase/admin pages may have their own helper separate from package/product price cards; audit both.
