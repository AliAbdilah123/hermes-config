# Currency + exchange-rate conversion tied to locale

When prices are stored in one base currency and the UI toggles
locale → currency + exchange rate, follow this pattern:

## Pitfall: verify which currency prices are stored in FIRST

**Do not assume.** Inspect real data. If prices look like `425000`, `500000`,
`575000` — they're almost certainly IDR (Rp), not USD. Converting the wrong
direction produces absurd results.

- **Prices stored in IDR** (komuna pattern): locale `id` → show as IDR (no
  conversion). Locale `en` → divide by rate to get USD.
- **Prices stored in USD**: locale `en` → show as USD (no conversion).
  Locale `id` → multiply by rate to get IDR.

## Design

1. **Separate locale detection from conversion**: `getCurrentLocale()` reads
   i18n locale from localStorage. `getUsdToIdrRate()` reads the rate from
   `import.meta.env.VITE_USD_TO_IDR_RATE`.

2. **Convert only when currency is implicit**: If the caller passes explicit
   `currency` (e.g., `{ locale: 'en', currency: 'USD' }`), assume the amount
   is already in that currency — skip conversion. Only convert when locale
   alone determines the currency:

```ts
// Prices stored in IDR. Convert IDR → USD when locale is not 'id'
// and no explicit currency was provided.
if (locale !== 'id' && !options?.currency) {
  const rate = getUsdToIdrRate()
  if (rate) {
    amount = amount / rate  // divide, not multiply
  }
}
```

This prevents double-conversion in callers like checkout `OrderSummaryCard`
that already resolve currency explicitly from locale.

## Why explicit-currency skips conversion

Callers fall into two categories:
- **Implicit**: `formatPriceLabel('500000', { locale: 'en' })` — locale alone
  picks USD; prices are stored in IDR → convert (divide by rate).
- **Explicit**: `formatPriceLabel('500000', { locale: 'en', currency: 'USD' })` —
  caller already resolved the amount to USD → no conversion.
The explicit path is used by checkout where the backend already returns
currency-resolved amounts.

## Rate source

Use `VITE_USD_TO_IDR_RATE` env var at build time. Extract from `.env` safely
without sourcing: `grep USD_TO_IDR_RATE .env | cut -d= -f2`. For vitest,
pass as shell env: `VITE_USD_TO_IDR_RATE=16000 npx vitest run` (see
`vite-env-vars-in-vitest.md`).

`vite-env-vars-in-vitest.md`).
