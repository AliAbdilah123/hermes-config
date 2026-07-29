# Full-stack preview verification boundaries

Use this when a feature spans schema/API/UI and the repository already has unrelated lint or test failures.

## Sequence

1. Run `git diff --check` and the complete owning backend suite from the module root.
2. If a regression appears in shared query/handler code, isolate the failing test, fix the shared contract, rerun that focused test, then rerun the complete backend suite from the final state.
3. Run full frontend lint/tests once to inventory baseline failures. Preserve exact totals and distinguish uncaught baseline runtime errors from feature failures.
4. Run ESLint only on changed TypeScript files. Git returns repository-relative paths; when executing from a nested package, strip the package prefix or run ESLint from repository root. An ESLint “no files matching” exit is invocation failure, not lint evidence.
5. Run focused UI suites that cover every changed flow, then rebuild. If deployment uses a preview subpath, rebuild again with the exact preview base and API base.
6. Report boundaries separately: diff hygiene, complete backend, full frontend baseline, changed-file lint, focused frontend, build, preview transport, rendered browser, authenticated flow, and production isolation.

## Isolated preview data/API

- Discover the production runtime database from the process environment or service definition.
- For live SQLite, use `.backup` or `VACUUM INTO`, then run `PRAGMA integrity_check` and prerequisite row counts.
- Run the feature API on a unique loopback port with the copied database.
- Proxy `/previews/<slug>/api/v1/` before the SPA location.
- Build with both the exact SPA base and preview API base; do not rely on HTML injection when compile-time environment variables govern requests.
- Verify public API returns JSON and deep routes return preview HTML containing the preview bundle hash.

## Browser evidence fallback

If the primary browser session times out, use installed headless Chromium with a bounded timeout, `--dump-dom`, and `--screenshot`. Capture stdout/stderr and exit status separately. Confirm artifacts exist before interpreting the exit code; inspect DOM for expected markers and absence of `Page not found`, and inspect stderr for `Uncaught`, console errors, or `net::ERR`. This proves rendering only—not authenticated feature behavior. Do not publish as approval-ready until prerequisite authenticated flows are exercised.