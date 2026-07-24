# Go + SQLite + Vite admin-settings rollout

Use this pattern when an administrative settings page must become the authoritative source for checkout calculations and historical reporting.

## Contract and persistence

- Keep one canonical monetary currency in storage and payment requests; treat alternate currencies as presentation-only conversions using a saved positive exchange rate.
- Normalize request aliases once at the API boundary, reject conflicting aliases, validate every field, then update the settings row and audit record in one transaction.
- Protect settings reads and writes with server-side platform-admin authorization; a guarded React route is not an API boundary.
- Put fee calculation in one server helper used by both quote and checkout initiation. Recalculate at initiation because a quote can become stale.
- Snapshot subtotal, fee, percentage, minimum, exchange rate, and currency on each purchase. Historical dashboards sum snapshots rather than recomputing old purchases using current settings.
- Explicitly mark legacy purchases whose snapshots are unavailable; do not present reconstructed values as exact.

## Activity queries

Return typed purchase data rather than preformatted activity sentences: purchase ID, buyer, program ID/name, every package ID/name, subtotal, fee, paid total, currency, status, and timestamp. Aggregate purchases and items separately or use correlated queries so joins to members/products/sessions cannot multiply revenue.

Use deterministic cursor ordering such as `(created_at DESC, purchase_id DESC)`. Provide an explicit Load more control even if IntersectionObserver also triggers it.

## Frontend handoff

- Lazy-load the route components and use a shell-sized Suspense skeleton; data loading needs its own skeleton/error/empty states.
- Bind the approved prototype to real DTOs and the existing shell/theme tokens rather than copying mock data or nested navigation chrome.
- Keep the currency toggle presentation-only and apply one formatter to metrics, program rows, activity, and settings previews.
- Disable payment when a valid server quote is unavailable instead of falling back to duplicated client fee constants.

## Verification and delivery

1. Add focused API tests for authorization, atomic validation, configured quote/checkout parity, snapshots, exact activity joins, and pagination.
2. Add focused UI tests for locale conversion, detailed purchases, settings payloads, lazy resolution, and quote-required checkout.
3. Run focused suites first, then typecheck and production build. Confirm separate lazy route chunks appear in build output.
4. Run broad suites independently. If an unrelated failure exists, capture its exact test name while keeping focused feature evidence distinct.
5. In a dirty repository, stage only task files and inspect the staged diff before commit. A clean commit does not prove a dirty-worktree build is deployable; use the clean-SHA build gate when unrelated changes can enter compilation.
6. Deploy the frontend artifact and API binary through the real runtime path, restart the service, then verify service health and the public route. HTTP 200 alone is not behavioral proof; use authenticated browser QA when available.

## Pitfalls

- Aggregate fee math such as `max(rate × total GMV, minimum × transaction count)` is wrong for mixed purchase prices.
- Updating settings without wiring checkout creates a decorative form, not functional settings.
- A route-level lazy import does not replace progressive loading for paginated activity.
- Do not let a coding delegate commit, deploy, or absorb unrelated dirty files; independently inspect its diff and execute final verification.
