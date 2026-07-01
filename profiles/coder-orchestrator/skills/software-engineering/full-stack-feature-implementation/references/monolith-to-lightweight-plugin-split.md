# Monolith to plugin-runtime restoration

Use when a copied SaaS implementation is still mostly monolithic, but the target project convention expects features to be composed as plugins.

## Choose the smallest split that satisfies the convention

1. **Route-composition split is enough** when the project only needs feature grouping and low-risk preservation of a working app:
   - Auth: login/logout/register/demo-login/current user.
   - Multi-tenant: config, tenant admin, tenant detail/settings/users/invites, notifications, audit logs.
   - Payment/Xendit: product catalog, purchases/payments/subscriptions, provider webhook/status normalization.
   - Add/keep a tiny local interface only if the branch has no stronger plugin runtime convention.
2. **Real runtime restoration is required** when the main branch already has a plugin framework or the user explicitly asks to follow `main` conventions:
   - Make feature plugins implement the existing `backend/core/plugin.Plugin` lifecycle (`Manifest`, `Init`, `Register`, `Start`, `Stop`).
   - Declare real manifest IDs, dependencies, and provided capabilities even if handler bodies remain in the old `App` temporarily.
   - Replace fake `ID()+RegisterRoutes()` interfaces with a `coreplugin.Plugin` registration path.
   - Add a small `plugin.Context` adapter if needed so existing `App` handlers can be registered through the runtime without immediately moving 1000+ lines of business logic.
   - Add tests that assert representative plugins implement `coreplugin.Plugin` and declare expected dependency IDs. This prevents a regression back to route-wrapper-only plugins.

## Minimal safe backend path

1. Write/extend tests first:
   - representative routes still return expected status;
   - each feature plugin satisfies `coreplugin.Plugin`;
   - manifests declare stable IDs and dependency order.
2. Convert feature plugin files to real plugin lifecycle methods.
3. Keep shared `App`, DB helpers, DTOs, migrations, and auth/session helpers in place until there is a strong need for package-level isolation. This avoids a risky large diff across a working app.
4. Use the existing framework's registry/capability/event/migration objects in the adapter context, even if some are initially unused. That keeps the seam compatible with later extraction.
5. Run `gofmt`, backend tests, and full app build/tests.

## Minimal safe frontend path

When a monolithic `App.tsx` replaced the frontend plugin runtime:

1. Restore the runtime files from `main` first: plugin interface, registry/resolver/bootstrap, route/nav/provider/slot registries, API client, event bus.
2. Preserve the working UI with a temporary `legacyAppPlugin` that registers the existing `App` as the root route.
3. Keep `AppShell` minimal while bridging: render registered routes and providers, but do not add a second shell/header around the legacy app.
4. Later, split the legacy app into feature frontend plugins route-by-route. Do not do this in the same risky pass unless necessary.
5. Verify frontend tests and production build, then deploy/curl the public SPA and grep the deployed JS for a marker from the restored runtime/plugin bridge.

## When to go further

Only physically extract handlers into independent Go packages when plugin ownership needs independent compilation, versioning, optional inclusion, or separate migrations. Otherwise route-composition plugins are the shortest diff that establishes the plugin boundary without destabilizing feature behavior.

If the user explicitly asks to continue toward the main-branch convention after a route-composition split, do the next smallest safe rung before a pure package rewrite:

1. Keep `package main` and move handler groups out of the giant `main.go` into plugin-owned files such as `plugin_auth_handlers.go`, `plugin_tenant_handlers.go`, and `plugin_payment_handlers.go`.
2. Preserve existing `App` method receivers and DB/config coupling during this pass; this shrinks the monolith without changing behavior.
3. Add/keep a compile-time test that the feature plugins implement the real core plugin interface and declare manifests/dependencies.
4. Run `gofmt`, `go test ./...`, frontend tests/build if the entrypoint/runtime changed, then compare line counts/diff stat to confirm the monolith actually shrank.
5. Only after this package-local extraction is green, consider the larger step: move files into `plugins/<feature>/backend`, split migrations, and replace `App` coupling with capability contracts.

Do not describe the first route-composition pass as “finished” when the requested convention includes full plugin package ownership; call it a safe first pass and state the remaining rungs clearly.

## Verification checklist

- `gofmt -w backend/cmd/app/*.go`
- `go test ./...`
- `npm test -- --run` (or the project-native test command)
- `npm run build`
- If deployed: copy fresh build artifacts to the actual nginx alias/root, curl the public index and assets, and verify a deployed JS marker from the plugin runtime/bridge.
- If an API service is deployed: curl public `/api/v1/health` and one plugin-owned route such as `/api/v1/config`.
