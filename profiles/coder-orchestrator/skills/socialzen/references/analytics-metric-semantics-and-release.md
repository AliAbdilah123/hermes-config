# Analytics metric semantics and release

Use when changing SocialZen analytics ingestion, aggregation, labels, ranking, exports, or historical metric repair.

## Semantic contract

- Preserve provider-native meanings. Threads `views`, `likes`, `replies`, `reposts`, `quotes`, and `shares` are distinct; never map views to reach/impressions or combine reposts+quotes into shares.
- Threads reach/impressions are unavailable. Its rate is **Engagements per view**, never a reach-based engagement rate.
- Facebook insight failures/missing values remain NULL/Unavailable; a confirmed provider zero remains numeric `0`. Preserve successful engagement counts when insights fail.
- Instagram's retry without impressions remains valid; do not make impressions mandatory.
- Cross-platform Total Reach sums only official supported reach. Expose provider-reported Views separately.
- Fail mixed-target rates closed unless numerator and denominator have the same attributable scope.
- Rank the complete post set by the selected metric, then slice Top Posts. Filter/sort tables before limiting, and include Threads.

## Cross-layer checklist

1. Add nullable native fields to both canonical schema declarations and idempotent migrations.
2. Thread fields through `TargetMetrics`, upsert SQL, analytics queries/DTOs, trends, exports, frontend types, capabilities, labels, details, tables, charts, and PDF output.
3. Repair contaminated historical Threads fields idempotently: clear legacy reach/impressions and derived shares, then let the normal refresh path repopulate native values. Ensure the cleanup also catches rows where only derived shares remains.
4. Add provider parser tests, aggregation/fail-closed tests, frontend capability/ranking tests, and changelog entry.

## Efficient verification

Run focused tests with direct Vitest file arguments; `npm test -- --run <files>` can be interpreted by this repository's script as a broad suite:

```sh
cd apps/backend-go
go test ./internal/threads ./internal/facebook
go test . -run 'TestAnalyticsSummary' -count=1 -timeout=60s
go build -o /tmp/socialzen-server .

cd ../frontend
pnpm exec vitest run src/lib/analytics.test.ts src/components/analytics/AnalyticsInsights.test.tsx
pnpm run typecheck
pnpm run build
```

Classify unrelated broad-suite failures separately; do not modify unrelated auth/settings behavior to make analytics work green.

## Deploy and public proof

- Install the freshly built backend binary, restart `socialzen.service`, and verify it is active.
- Rsync the fresh frontend `dist/` to `/var/www/html/projects/socialzen/`.
- Compare the local and cache-busted public `assets/index-*.js` hash.
- Require HTTP 200 for `/api/health` and `/app/analytics`.
- Inspect the deployed analytics chunk for the new user-visible labels when browser automation is unavailable. This proves artifact contents, not authenticated interaction; do not overstate it as full authenticated E2E.
