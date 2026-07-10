# Checkout UI currency + deployment notes

Use when fixing Komuna checkout/package purchase pages where prices, locale switching, or above-the-fold density are involved.

## Durable lessons

- Checkout prices can arrive as IDR-base strings that already include a symbol (example: `$600000`). Do not trust a leading symbol as proof the value is already localized. Parse the numeric value and let the shared pricing formatter/localization path decide display currency.
- For English locale, Komuna uses `VITE_USD_TO_IDR_RATE` (currently present in `apps/web/.env`) to convert IDR amounts to USD. Tests should set this env var explicitly for deterministic expectations.
- Avoid passing an explicit currency into `formatPriceLabel` when the desired behavior is locale-driven conversion; explicit currency can bypass conversion and preserve the wrong unit.
- Compact checkout pages should be verified at a real desktop viewport (e.g. 1440x900) with the product hero, package title/details, order summary, and Pay button visible without unnecessary scrolling.
- Keep payment CTA copy gateway-neutral (`Pay` / `Bayar`) unless the user explicitly asks to expose the provider name.

## Verification pattern

1. Run targeted checkout/pricing tests with an explicit rate, then build:
   `VITE_USD_TO_IDR_RATE=16000 npx vitest run src/__tests__/pricing.test.ts src/__tests__/CheckoutPage.test.tsx && unset VITE_NEON_AUTH_URL && npm run build`
2. Deploy the built frontend from `apps/web/dist/` to the Komuna nginx web root (`/var/www/html/projects/komuna/`) with rsync, then chown to `www-data:www-data`.
3. Smoke the live checkout URL and asset URL with `curl -sI`.
4. Use a headless screenshot or browser visual check at 1440x900 to verify above-the-fold layout and localized price display.
5. Commit and push only the intended source/test files; avoid sweeping unrelated docs/plans/backups into the commit.
