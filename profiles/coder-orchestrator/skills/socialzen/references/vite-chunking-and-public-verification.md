# Vite chunking and public verification

Use when SocialZen's production build emits `Some chunks are larger than 500 kB` or when changing `manualChunks`.

## Diagnose first

1. Run `npm run build` from `apps/frontend` and retain the complete asset-size table.
2. Inspect `vite.config.ts` before changing imports. A catch-all `if (id.includes("node_modules")) return "vendor-common"` can defeat route-level lazy loading by merging unrelated dependencies.
3. Treat the warning as an actual threshold failure; do not merely increase `chunkSizeWarningLimit`.

## Minimal fix pattern

- Keep deliberate chunks for cohesive heavy dependencies used together.
- Split independently loadable heavy tools, e.g. `jspdf` and `html2canvas`, rather than forcing both into one PDF chunk.
- Remove catch-all vendor grouping and let Rollup retain remaining dependencies with their lazy route.
- Do not add a chunking plugin unless native Rollup configuration cannot solve the measured issue.

## Verification

From `apps/frontend`:

```sh
npm run typecheck
npm test -- --run <focused-tests>
npm run build 2>&1 | tee /tmp/socialzen-build.log
! grep -q 'Some chunks are larger than' /tmp/socialzen-build.log
MAX=$(find dist/assets -type f -name '*.js' -printf '%s\n' | sort -nr | head -1)
test "$MAX" -lt 512000
```

Then deploy the fresh `dist/` via the standard SocialZen frontend workflow.

Public proof must include all of:

1. Cache-busted HTML from `https://dev-socialzen.ahsanworks.com/...` references the same `assets/index-*.js` hash as local `dist/index.html`.
2. Newly split chunks return HTTP 200.
3. The obsolete catch-all chunk is absent from the deployed asset directory.
4. `socialzen.service` remains active.

Do not assume `socialzen.ahsanworks.com` and `dev-socialzen.ahsanworks.com` serve the same artifact; verify the configured/default project domain and report the one whose bundle matches local output.
