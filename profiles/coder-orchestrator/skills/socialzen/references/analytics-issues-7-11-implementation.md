# Analytics Issues 7–11 Implementation Pattern

Use this when provider-safe analytics is already in place and the remaining work concerns unavailable metrics, account disconnects, refresh outcomes, ranking visualization, or clickable insight references.

## Behavior

1. **Unavailable provider metrics remain nullable**
   - Preserve unsupported/missing provider values as `NULL` through storage and DTO mapping.
   - Render `Unavailable` in post detail rather than coercing missing values to `0`.
   - Keep real zero distinct from unavailable.

2. **Referenced account disconnect is non-destructive**
   - If an Instagram account is referenced by historical posts/targets, soft-disconnect it instead of deleting the row.
   - Exclude inactive accounts from connected-account listings and selection UI.
   - Preserve the row so historical analytics and exact target identity remain resolvable.
   - Keep migration definitions synchronized in both production `internal/models.Migrate()` and test/legacy `app.migrate()` paths.

3. **Refresh reports aggregate outcome honestly**
   - Track provider/target refresh attempts and classify the request as success, partial success, or failure.
   - Do not report success merely because one provider succeeded if another failed.
   - Log provider failures for diagnosis, but redact tokens, credentials, and credential-like query/body values.

4. **Ranking and insight navigation stay client-side**
   - Build Top Posts ranking from the already-filtered analytics response; do not add another backend query.
   - Allow only supported ranking metrics and make bars clickable to open the existing analytics post-detail modal.
   - Make What Worked post references clickable through the same modal callback.
   - Preserve the existing create-similar-post route/action.

## Focused verification

```bash
cd apps/frontend
pnpm exec vitest run src/lib/analytics.test.ts src/components/analytics/AnalyticsInsights.test.tsx
pnpm typecheck
pnpm build

cd ../backend-go
go test . -run 'Test(Analytics|InstagramAccount)' -count=1
go test ./internal/models ./internal/facebook ./internal/posts
go build ./...
```

After deployment, verify the analytics chunk itself, not only `index.html`:

```bash
asset=$(basename $(find /var/www/html/projects/socialzen/assets -name 'AnalyticsPage-*.js' -print -quit))
curl -fsSI "https://socialzen.ahsanworks.com/projects/socialzen/assets/$asset" | grep -Ei '^(HTTP|content-type:|cf-cache-status:)'
grep -Eo 'Top Posts|Unavailable|What Worked' "/var/www/html/projects/socialzen/assets/$asset" | sort -u
```

Expected public asset content type: `application/javascript`.

## Delivery pitfall

The SocialZen working tree may contain unrelated in-progress changes. Stage the approved analytics file allowlist explicitly, run `git diff --cached --check`, then commit/push only that scope. Do not use broad `git add -A` for this workflow.
