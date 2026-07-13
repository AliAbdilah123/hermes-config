# Locale-aware money formatting and live i18n rerenders

Use when a user reports money displays the wrong currency/symbol after a locale toggle, especially in React/Vite apps.

## Root-cause pattern

Money values may be stored in a base currency (for Komuna: IDR) while English UI displays converted USD. Bugs often come from one of two layers:

1. A new formatter hardcodes `en-US` + `USD`, bypassing the shared locale-aware formatter.
2. A component calls a locale-aware formatter but does not subscribe to i18n state, so toggling language updates storage/i18n globally but the component does not rerender.

## Debug checklist

1. Search all money formatting paths for `Intl.NumberFormat`, `toLocaleString`, currency literals (`USD`, `IDR`, `Rp`, `$`), and page-local helper functions.
2. Identify the canonical shared formatter and the data's stored base currency before changing math.
3. Add a formatter unit test for the exact reported amount in both locales.
4. Add a UI regression test that changes language via `i18n.changeLanguage(...)` and asserts the already-rendered component updates without reload.
5. In React components, call `useTranslation()` (or an existing i18n hook) in the component that renders the money, and pass `i18n.language` explicitly to the formatter. Reading `localStorage` inside a formatter is not enough to trigger rerender.
6. Verify build/typecheck because tests often use partial DTO fixtures that must satisfy TypeScript when `tsc -b` includes test files.

## Minimal fix shape

```tsx
const { i18n } = useTranslation()

<strong>{formatCurrencyAmount(purchase.total_amount, i18n.language)}</strong>
```

Keep conversion logic in one shared helper; do not duplicate `Number(...).toLocaleString('en-US', { currency: 'USD' })` in pages.
