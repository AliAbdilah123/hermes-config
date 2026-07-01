# Boilerplate Plugin Anatomy

Quick reference for adding a new plugin to the multi-tenant auth SaaS boilerplate. Use this when planning or implementing any new feature as a plugin.

## Plugin directory structure

```
plugins/<name>/
├── backend/
│   ├── plugin.go          # struct, Manifest, Init/Register/Start/Stop
│   ├── handlers.go        # HTTP handlers (or split per domain)
│   ├── <domain>.go        # domain logic (credits.go, provider.go, etc.)
│   └── migrations/
│       └── NNN_name.sql   # CREATE TABLE + indexes
└── frontend/
    └── src/
        ├── plugin.ts      # FrontendPlugin registration
        ├── types.ts       # API response types
        ├── <Page>.tsx     # route components
        └── *.test.tsx     # frontend tests
```

## Backend plugin contract

```go
type Dependencies struct {
    DB           *sql.DB
    Config       Config
    // ... other deps injected at composition time
    AddMigration func(plugin.Context, string, string, string) error
    JSONHandler  func(func(*http.Request) (any, int)) http.HandlerFunc
    WriteJSON    func(http.ResponseWriter, int, any)
    WriteError   func(http.ResponseWriter, int, string)
    DecodeJSON   func(http.ResponseWriter, *http.Request, any) bool
}

func (p Plugin) Manifest() coreplugin.Manifest {
    return coreplugin.Manifest{
        ID:       "com.boilerplate.<name>",
        Name:     "Human Name",
        Version:  "1.0.0",
        Requires: []coreplugin.Dependency{{ID: "com.boilerplate.auth.basic", Version: ">=1.0.0"}},
        Provides: []string{"<capability>"},
    }
}
```

## Wiring into the app

Two files to modify in `backend/cmd/app/`:

### 1. `plugin_<name>.go` — plugin factory

```go
func (a *App) <name>Plugin() <pkg>.Plugin {
    return <pkg>.New(<pkg>.Dependencies{
        DB: a.db, Config: <pkg>.Config{...},
        AddMigration: addEmbeddedMigration,
        JSONHandler: jsonHandler, WriteJSON: writeJSON,
        WriteError: writeError, DecodeJSON: decodeJSON,
    })
}
```

### 2. `main.go` — register in two places

```go
// In routes():
registerPlugins(a, mux,
    a.authPlugin(),
    a.multiTenantPlugin(),
    a.<name>Plugin(),  // ADD HERE
)

// In migrate():
registerPluginMigrations(ctx, db, app,
    app.authPlugin(),
    app.multiTenantPlugin(),
    app.<name>Plugin(),  // ADD HERE
)
```

## Frontend plugin contract

```typescript
// plugin.ts
export default {
  manifest: { id: "com.boilerplate.<name>", name: "...", version: "1.0.0",
    requires: [{ id: "com.boilerplate.auth.basic", version: ">=1.0.0" }] },
  register(ctx: FrontendPluginContext) {
    ctx.routes.add({ path: "/<path>", component: <Page> })
    ctx.slots.add("topbar", <Badge />)
  }
}
```

### Wire into `frontend/src/App.tsx`

```tsx
import <name>Plugin from '../../plugins/<name>/frontend/src/plugin'
const plugins = [authPlugin, multiTenantPlugin, <name>Plugin]
```

## Key conventions

- **Migrations**: embedded with `//go:embed migrations/*.sql`, registered via `addEmbeddedMigration` helper that feeds into `MigrationRegistry`.
- **Routes**: registered in `Register()` via `ctx.Router().HandleFunc(...)`.
- **Capabilities**: provided in `Init()` via `ctx.Capabilities().Provide("name", impl)`.
- **Auth**: use `ctx.Services().Auth().RequireAuth(w, r)` to get `services.AuthedRequest`.
- **Tenant scoping**: all tenant-owned data queries include `WHERE tenant_id = ?` scoped to the authenticated user's tenant.
- **JSON helpers**: use `deps.JSONHandler()` to wrap endpoint functions returning `(any, int)`.
- **Config**: env vars read per-plugin; pass needed values through the plugin's `Config` struct in the factory function.

## No-auth / public endpoints

If a plugin needs public (unauthenticated) endpoints, don't call `RequireAuth` — just register the route directly. The CORS middleware is already applied globally in `routes()`.
