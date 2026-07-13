# Purchase currency and responsive purchases table

Use when Komuna purchase totals/revenue display the wrong currency, do not update when the language toggle changes, or the admin Purchases table breaks on narrow screens.

## Currency root-cause pattern

Komuna stores purchase/package amounts as IDR numeric strings. Frontend components must not format purchases directly with `toLocaleString('en-US', { currency: 'USD' })`; that displays IDR cents/amounts as giant USD values (for example `7410000` becomes `$7,410,000`).

Use the shared pricing path instead:

- `formatPriceLabel(value, { locale })` for raw prices/packages.
- `formatCurrencyAmount(value, locale)` for purchase totals/revenue; it should delegate to `formatPriceLabel`.
- Do not rely only on `localStorage` inside a formatter for live UI updates. Components that must update when the language toggle changes need `useTranslation()` and should pass `i18n.language` into the formatter.

Regression shape:

```ts
vi.stubEnv('VITE_USD_TO_IDR_RATE', '16000')
expect(formatCurrencyAmount(7410000, 'en')).toBe('$463.13')
expect(formatCurrencyAmount(7410000, 'id')).toContain('Rp')
```

For live-toggle UI tests, render under `I18nextProvider`, assert the English amount, then `await act(async () => { await i18n.changeLanguage('id') })` and assert the `Rp` amount appears without remounting.

## Responsive Purchases table pattern

If the admin Purchases table is clipped or squeezed on mobile, add horizontal scroll only around the table content, not around the filters.

Minimal structure:

```tsx
<section>
  <div data-testid="admin-purchases-filters">...</div>
  <div data-testid="admin-purchases-table-scroll" style={{ overflowX: 'auto' }}>
    <div data-testid="admin-purchases-table" style={{ minWidth: 980 }}>...</div>
  </div>
</section>
```

Keep the filter row as a sibling before the scroll wrapper so search/status/date filters do not move horizontally with table columns. Verify with a test that the filters' parent is not the scroll element, the scroll element has `overflowX: auto`, and the inner table has a desktop `minWidth`.
