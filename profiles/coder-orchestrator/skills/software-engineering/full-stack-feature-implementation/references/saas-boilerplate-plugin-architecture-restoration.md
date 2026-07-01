# SaaS boilerplate plugin architecture restoration

Use when a copied SaaS boilerplate branch claims to be pluginized but still has a monolithic Go backend and/or deleted frontend plugin runtime.

## Durable pattern from the boilerplate session

1. **Diagnose against `main` conventions first**
   - Compare branch structure to `main` using `git ls-tree` / diffs.
   - Real backend plugins should implement `backend/core/plugin.Plugin`: `Manifest`, `Init`, `Register`, `Start`, `Stop`.
   - Real frontend plugins should use `FrontendPlugin`, route/nav/slot/provider registries, and bootstrap through `frontend/src/runtime/bootstrap.tsx`.
   - Thin files that only call `mux.HandleFunc` while all logic stays in `main.go` are route wrappers, not real plugin ownership.

2. **Do the smallest safe restoration before full package extraction**
   - Add tests first that assert feature plugins implement `coreplugin.Plugin` and declare expected manifest IDs/dependencies.
   - Replace local fake plugin interfaces with `coreplugin.Plugin` registration through a tiny app-specific `pluginContext` adapter when the app still owns `App`, DB, and config.
   - Keep handlers in the existing package initially to avoid a risky cross-package rewrite; this restores lifecycle and dependency metadata while preserving behavior.

3. **Restore frontend runtime without breaking the current UI**
   - Bring back deleted runtime files from `main`: `api`, `events`, `layout`, `nav`, `providers`, `routing`, `runtime`, and `slots`.
   - If the UI is still monolithic, register it temporarily through a `legacyAppPlugin` and render routes via a minimal `AppShell`. This keeps tests/build green while enabling later route-by-route frontend plugin extraction.

4. **Physically move code out of `main.go` inside the package next**
   - Split functions into feature-owned files such as `plugin_auth_handlers.go`, `plugin_tenant_handlers.go`, and `plugin_payment_handlers.go` before moving to separate Go packages.
   - This quickly exposes boundaries and reduces `main.go` while avoiding import cycles around `App`.

5. **Split migrations with a regression test**
   - Write a failing test that checks expected split migration files exist and that `migrate()` creates auth/tenant/payment tables.
   - Replace a monolithic SQL file with ordered feature files, e.g. `001_auth.sql`, `002_multi_tenant.sql`, `003_xendit_payment.sql`.
   - Preserve table definitions needed by existing seed/tests; if previous runtime had compatibility shims like `ensureMutableCatalogSchema`, include those columns directly in the new migration.
   - After file splitting, register those embedded SQL files from each plugin's `Register(ctx)` via `ctx.Migrations().Add(...)`, and add a regression test that applies through `coredb.MigrationRegistry` and verifies `core_plugin_migrations` rows. This proves migrations are plugin-owned, not merely app-owned files.

6. **Verify after each rung**
   - `go test ./...`
   - project-native frontend tests (do not add runner flags the repo does not use)
   - `npm run build`
   - if deployed, copy built frontend assets and verify a deployed JS marker.

## Pitfalls

- Do not jump straight to separate Go packages when all handlers depend on a package-local `App` type; it creates import-cycle risk and large diffs. Restore lifecycle/manifest boundaries first, then file boundaries, then package boundaries.
- Do not call the work “finished” after lifecycle restoration if handlers still depend on shared `App`, migrations are monolithic, or frontend is still a legacy plugin. Report the remaining boundary work explicitly.
- When using `git checkout main -- frontend/src/runtime/...`, remember those added files may be staged in the index; use `git diff HEAD --stat` / `git status --short` to see the full change set.
