# Monolith to lightweight plugin split

Use when a copied SaaS implementation is still mostly monolithic, but the target project convention expects features to be composed as plugins.

## Minimal safe split

1. Map feature boundaries by route first, before moving large handler bodies:
   - Auth: login/logout/register/demo-login/current user.
   - Multi-tenant: config, tenant admin, tenant detail/settings/users/invites, notifications, audit logs.
   - Payment/Xendit: product catalog, purchases/payments/subscriptions, provider webhook/status normalization.
2. Add a tiny plugin interface near the app composition layer:
   - `ID() string`
   - `RegisterRoutes(app *App, mux *http.ServeMux)`
3. Move route registration into feature plugin files such as `plugin_auth.go`, `plugin_multitenant.go`, and `plugin_xendit_payment.go`.
4. Keep shared `App`, DB helpers, DTOs, migrations, and auth/session helpers in place until there is a strong need for package-level isolation. This avoids a risky large diff across a working app.
5. Add a small backend regression test that starts the app and checks representative routes from each plugin return the expected status.
6. Run full backend tests, frontend tests/build if public behavior may be affected, then rebuild/restart the deployed service and smoke the public API prefix.

## When to go further

Only physically extract handlers into independent Go packages when plugin ownership needs independent compilation, versioning, optional inclusion, or separate migrations. Otherwise route-composition plugins are the shortest diff that establishes the plugin boundary without destabilizing feature behavior.

## Verification checklist

- `gofmt -w backend/cmd/app/*.go`
- `go test ./...`
- `npm test` and `npm run build` if the SPA is part of the deployed artifact
- Rebuild/install API binary, restart systemd service, check `systemctl is-active`
- `curl` public `/projects/<slug>/api/v1/health` and at least one plugin-owned route such as `/api/v1/config`
