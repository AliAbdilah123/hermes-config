# Frontend route namespace migrations

Use when moving an existing SPA application's authenticated/product routes beneath a prefix such as `/app`, while replacing `/` with a public landing page.

## Implementation checklist

1. Inventory every filesystem-backed route and move all application pages beneath the new namespace; leave the root layout and new public root page outside it.
2. Update internal navigation at the source level (`resolve`, `goto`, links, redirects, active-route checks), while leaving backend API paths unchanged.
3. Update layout classification so `/` and account routes render without the authenticated app shell.
4. Search tests for hard-coded source fixture paths as well as URL assertions. Route moves often break tests that read component files directly even when runtime navigation is correct.
5. Add one structural regression check proving:
   - `/` contains landing-page content and links into the namespaced app;
   - no app navigation still targets the old top-level route set.
6. Run the full sequence: tests, framework/type check, production build. A passing build alone does not catch stale test fixture paths.
7. Inspect the staged diff so route moves are recognized as renames rather than accidental delete/recreate churn, then commit and push only intended files.

## Common pitfalls

- A global route-literal replacement can correctly update application links but miss strings that name files, such as `src/routes/notes/+page.svelte` in source-inspection tests.
- Do not prefix `/api/...`; the UI namespace and backend API namespace are separate contracts.
- After moving routes, generated framework route types may remain stale until the framework sync/check command runs.
- The root landing page must be explicitly treated as public; otherwise the authenticated shell may wrap it and trigger profile/session behavior.
