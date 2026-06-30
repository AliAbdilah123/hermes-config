# Go Plugin Route Splitting

Use when the user asks to separate features into plugins in a Go + ServeMux backend that has a monolithic `routes()` method with all handlers on a shared `App` struct.

## When to use

- The backend is a single-package `main.go` (or few files) with all route registrations in one `routes()` method.
- Full extraction into separate Go packages would require moving shared types, DB access, and handler methods — too much churn for the asked-for separation.
- The goal is feature-level route ownership and composability, not independent compilation.

## Pattern

1. Define a minimal plugin interface in a new file (e.g. `plugins.go`):

```go
type appPlugin interface {
    ID() string
    RegisterRoutes(app *App, mux *http.ServeMux)
}

func registerPlugins(app *App, mux *http.ServeMux, plugins ...appPlugin) {
    for _, p := range plugins {
        p.RegisterRoutes(app, mux)
    }
}
```

2. Create one file per feature (e.g. `plugin_auth.go`, `plugin_multitenant.go`, `plugin_xendit_payment.go`):

```go
type authPlugin struct{}

func (authPlugin) ID() string { return "auth" }

func (authPlugin) RegisterRoutes(app *App, mux *http.ServeMux) {
    mux.HandleFunc("/api/v1/auth/login", app.login)
    mux.HandleFunc("/api/v1/auth/register", app.register)
    mux.HandleFunc("/api/v1/me", app.me)
}
```

3. Replace the inline route registrations in `routes()` with a `registerPlugins` call:

```go
func (a *App) routes() http.Handler {
    mux := http.NewServeMux()
    mux.HandleFunc("/api/v1/health", ...)  // keep core/health in routes()
    registerPlugins(a, mux,
        authPlugin{},
        multiTenantPlugin{},
        xenditPaymentPlugin{},
    )
    return middlewareChain(mux)
}
```

4. Add a test that verifies plugin routes are reachable:

```go
func TestFeaturePluginsExposeExpectedRoutes(t *testing.T) {
    _, server := newTestServer(t)
    checks := map[string]int{
        "/api/v1/auth/demo-login": http.StatusOK,
        "/api/v1/config":          http.StatusOK,
    }
    for path, want := range checks {
        resp, _ := getJSON(t, server, path, "")
        if resp.StatusCode != want {
            t.Fatalf("%s status=%d want=%d", path, resp.StatusCode, want)
        }
    }
}
```

## Benefits

- Each feature's routes are in one file, easy to find and reason about.
- Adding/removing a feature = adding/removing one struct from the composition list.
- No package boundary churn — handlers stay on `App`, sharing DB and config naturally.
- Test can assert which routes each plugin contributes.

## When to go further (full package extraction)

- When plugins need independent versioning or compilation.
- When different plugins should use different DB connections or config.
- When the team needs strict ownership boundaries (separate PR review, separate test suites).

Until those needs arise, the interface+route-file pattern is the right ceiling. Mark with a `// ponytail: route-level plugin split; extract to packages when independent compilation is needed` comment if desired.
