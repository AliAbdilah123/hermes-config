# delegate backend refactor

## Before
`backend/cmd/api/main.go` — 2,653 lines, one package. Contained:
- `Config` struct + env loading
- 11 model structs
- `App` struct
- 48+ handler / query methods
- `migrate`, `seed*` functions
- `embed.FS` migrations + `//go:embed`
- helpers (`hashPassword`, `verifyPassword`, `randomToken`, `sortSQL`, etc.)

## Target
Split into `backend/internal/app/` (same module) because:
1. Go `internal` is only accessible within the same module
2. `cmd/api/internal/app/` does not satisfy sibling import paths like `github.com/.../backend/internal/helpers`
3. Existing module is `github.com/AliAbdilah123/multitenant-auth-saas-boilerplate/backend`

## Files written

| File | Responsibility |
|------|----------------|
| `types.go` | App struct + 11 model structs + endpoint type |
| `config.go` | Config struct, LoadConfig, loadDotEnv, firstEnv, env |
| `helpers.go` | hashPassword, verifyPassword, pbkdf2Key, randomToken, tokenHash, bearerToken, decodeJSON, writeJSON, writeError, normalizeEmail, validSlug, sortSQL, sortDirSQL, tenantScopedSlug, publicSlug, boolInt, normalizeXenditPaymentStatus, validTaskStatus, normalizeTaskStatus, nullIfEmpty, tenantExists, nullInt |
| `app.go` | NewApp, Routes, jsonHandler, cors, requestLog, requireAuth, createSession, memberships, membershipForTenant, canAccessTenant, canAdminTenant, insertAudit, userInTenant, notificationVisibleToUser, recordWelcomeEmail |
| `handlers_auth.go` | login, logout, register, registerSelfServe, registerWithInvite, me |
| `handlers_tenants.go` | tenants, getTenant, adminTenants, adminUsers, updateTenantSettings, listTenantUsers, createInvite |
| `handlers_notifications.go` | notifications, composeNotification, listNotifications, markNotificationRead |
| `handlers_audit.go` | auditLogs + query builder |
| `handlers_catalog.go` | products, createPurchase, listPayments, listSubscriptions, xenditWebhook, tenantProducts, tenantPlans, createProduct, updateProduct, createPlan, updatePlan, deletePlan, normalizePlanRequest, catalog helpers, All catalog queries |
| `handlers_delegation.go` | ensureDelegationSeed, delegationWorkspace, listProjects, listTeamUsers, listDelegatedStatuses, listDelegatedGroups, listTasks, listTaskMessages, listAIRuns, projectIDsForTask, projectsAPI, tasksAPI, taskAPI, aiUsersAPI, taskMessagesAPI, testAIForwarder |
| `xendit.go` | gatewayInvoice, paymentGateway, mock/real gateways |
| `migrations.go` | embed.FS + Migrate, ensureMutableCatalogSchema, columnExists, SeedSuperAdmin, seedDemoData, seedDemoProducts, seedDemoTenantsUsers, seedDemoSubscriptions, insertUser, insertAuditTx |

## Critical gotcha
`SeedSuperAdmin` called `hashPassword`, `normalizeEmail`, `tenantExists`, `tenantScopedSlug`. These helpers live in `internal/app/helpers.go`. Since `migrations.go` is in the same `package app`, every helper in `helpers.go` is visible unqualified. No extra package import needed.

## Runtime
Binary built and health-checked on `:19090`. Endpoint responded:
```json
{"locale_default":"id","service":"multitenant-auth-saas-boilerplate","status":"ok"}
```
