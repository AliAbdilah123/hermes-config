# Shared analytics placement and filter verification

Use when one analytics visualization appears on multiple pages, or when a chart must follow another chart's period controls.

## Contract to verify

1. Keep aggregation reusable, but let each page supply its period (`start`, `end`, or already-filtered records).
2. On an analytics page, derive both charts from the same completed/paid-order range. Do not let a reusable chart silently retain its own fixed lookback when page filters exist.
3. Keep the fixed lookback only on surfaces that have no period controls (for example, a catalog overview).
4. Test DOM order explicitly with `compareDocumentPosition`: the required preceding chart must be followed by the dependent chart.
5. Seed one sale inside the default range and one outside it but inside a broader range. Assert the second item is absent initially, change the period filter, then assert it appears. This proves filter propagation rather than merely checking chart presence.
6. For custom ranges, verify invalid dates suppress or empty the dependent visualization consistently with the rest of the analytics page.
7. Make the chart's title and accessible name reflect whether it is a fixed lookback or selected period; avoid announcing “last 30 days” when a 7-day/custom filter is active.
8. After deployment, run a public browser probe that checks chart order and changes a real period control. A health check and static presence assertion are insufficient.

## Common pitfall

Passing all orders into a shared chart while separately filtering headline metrics creates contradictory analytics. Prefer passing the page's filtered order set plus explicit range boundaries, so bars, legend, quantities, and totals share one source of truth.
