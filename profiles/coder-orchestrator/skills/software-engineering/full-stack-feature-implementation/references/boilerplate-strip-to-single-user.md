# Boilerplate strip to single-user app

Use this when creating a new project from the multi-tenant SaaS boilerplate that should be single-user (no tenants, no memberships, no payments). The new project keeps the plugin runtime + auth-basic, strips everything else, and wires a new domain plugin.

## Proven workflow

### 1. Seed from boilerplate safely
```bash
rsync -a --exclude='.git' --exclude='node_modules' --exclude='dist' \
  --exclude='sqlite.db' --exclude='*.db-shm' --exclude='*.db-wal' \
  /home/ubuntu/projects/boilerplate/ /opt/<new-project>/
```

### 2. Delete unused plugins
Remove these directories from `plugins/`:
- `multi-tenant/`
- `payment/`
- `stripe/`
- `stripe-subscription/`
- `xendit-payment/`
- `ai-core/`

### 3. Update module path
Change `go.mod` module from `example.com/plugin-runtime` to the new project name. Update all Go import paths across the project.

### 4. Strip Config struct in `backend/cmd/app/main.go`
Remove: `SeedSuperAdminTenant`, `XenditSecret`, `XenditAPIBase`, `XenditWebhookToken`, `ResendAPIKey`, `ResendFromEmail`.
Remove type aliases: `Product`, `Plan`, `Payment`, `Subscription`.
Remove `Notification`, `AuditLog` type aliases (living with multi-tenant plugin).
Remove `seedSuperAdmin()` call.
Remove `ensureMutableCatalogSchema()`.

### 5. Delete tenant/payment/AI plugin wiring files
Remove from `backend/cmd/app/`:
- `plugin_multitenant.go`
- `plugin_tenant_handlers.go`
- `plugin_xendit_payment.go`
- `plugin_ai_core.go`
- `ai_core.go`

### 6. Simplify plugin registration
In `routes()`: register only `authPlugin()` (and new domain plugin later).
In `migrate()`: register only `authPlugin()` (and new domain plugin later).

### 7. Simplify `plugin_auth_handlers.go`
Remove from struct:
- `Memberships` func
- `MembershipForTenant` func
- `RecordWelcomeEmail` func
- `InsertAuditTx` func
- All multi-tenant helper methods (`memberships`, `membershipForTenant`, `insertAuditTx`)
Keep: `requireAuth`, `createSession`, `insertUser`, hash helpers.

### 8. Slim `backend/core/services/services.go`
Keep only: `User`, `AuthedRequest`, `AuthService`.
Remove: `Tenant`, `Membership`, `Product`, `Plan`, `Payment`, `Subscription`, `TenantService`, `PaymentService`, `AppServices`.

### 9. Simplify `appServices` in `plugins.go`
Remove `Tenants()` and `Payments()` methods. Only `Auth()` remains.

### 10. Simplify auth registration
In `plugins/auth-basic/backend/handlers.go`:
- Remove `TenantName`, `TenantSlug`, `InviteToken` from register request struct
- Replace `registerSelfServe`/`registerWithInvite` with simple user creation (INSERT into users + create session)

### 11. Frontend cleanup

**`App.tsx`**: Remove all plugin imports except `authPlugin`.

**`AppShell.tsx`**: Remove:
- `canManage`, `canManageAnyTenant` imports/usage
- `Product` import
- `selectedProduct` state
- `productDetail` route case
- Super admin role gating (redirect guard, nav filtering)

**Auth frontend types** (`plugins/auth-basic/frontend/src/types.ts`): Remove `Membership`. `Session = {token, user}`, `AuthResponse = {token, user}`.

**AuthModal**: Remove tenant_name/tenant_slug fields from signup form.

**`vite.config.ts`**: Update `base` to `/projects/<new-project>/`.

**`package.json`**: Update `name`.

**`index.html`**: Update `<title>`.

**`scripts/smoke.sh`**: Update `PROJECT` default.

### 12. Verify clean build
```bash
cd /opt/<new-project> && go build ./...
cd /opt/<new-project> && npm run build
```

## Pitfalls

- **AppShell references auth plugin types directly** (e.g. `AuthMode`, `AvatarMenu`, `NavItem`, `canManageAnyTenant`). When stripping, remove these imports from AppShell.tsx.
- **Auth plugin frontend references `memberships`** in SessionProvider, AuthModal, types.ts. All must be stripped.
- **Go build will fail** if any `.go` file still imports stripped packages (multi-tenant, payment). Use `go build ./...` to catch all.
- **Module path rename** — search across ALL files (Go, TSX) for old import paths. The frontend plugin imports use relative paths (`../../../../frontend/src/...`) so they survive the Go module rename, but `App.tsx` imports plugins directly.
- **services.go** — if you remove `AppServices` interface but `plugins.go` still implements it, the build fails. Update `appServices` struct to match.
