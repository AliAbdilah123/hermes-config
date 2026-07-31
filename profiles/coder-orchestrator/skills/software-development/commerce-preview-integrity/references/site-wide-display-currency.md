# Site-wide display-currency verification

Use when an IDR/USD selector must affect the whole commerce experience while canonical transactions remain IDR.

## Root-cause audit

1. Trace the selector through storage/state, its change event, and the React subscription that rerenders active routes. A formatter reading `localStorage` is not enough by itself.
2. Inspect the actual preview build environment. If conversion depends only on a missing build-time rate, the UI may accept USD while formatters silently fall back to IDR.
3. Prefer an API-provided platform rate for quote, analytics, and dashboard DTOs. For surfaces without one, use one documented shared display-rate fallback—not page-local constants.
4. Search active routed code for bypasses: `Intl.NumberFormat`, `toLocaleString`, `Rp`, `IDR`, `USD`, `$`, compact chart labels, and local price helpers.
5. Exclude non-display semantics: money inputs, settings labels, canonical DB amounts, quote/invoice/provider currency, IDs, counts, fixtures, and intentionally inert prototypes.

## Regression matrix

Write failing tests first and observe RED. Cover representative surfaces rather than only the toggle:

- discovery/program card: IDR → USD → IDR live, without reload;
- product/package detail or booking choice;
- checkout subtotal, fee, and total using the quote rate;
- member purchase/wallet display;
- admin revenue card and compact chart labels;
- analytics tables and platform dashboard;
- checkout request assertions proving no `displayCurrency` or substituted transaction `currency` enters provider/API payloads.

Tests must mount a real currency subscription boundary (normally the app root). Calling a formatter after changing storage does not prove mounted UI rerenders.

## Public proof

On the exact deployed preview:

1. Record a visible commercial amount in IDR.
2. Change to USD through the preference UI when authentication is available; otherwise use the same public-page state event only as supporting route evidence.
3. Confirm the existing DOM changes to the mathematically expected USD value without reload.
4. Change back to IDR and confirm restoration.
5. Exercise an authenticated dashboard route separately. Component tests are supporting evidence, not public dashboard E2E.
6. Report the effective rate and clearly state that stored prices, checkout payloads, invoices, and provider currency remain canonical IDR.

Do not call the feature fixed because the selector's pressed state or `localStorage` value changes. Acceptance requires visible money changing on representative commercial and dashboard surfaces.
