# Go Layered Architecture — Migration Dead-Code Trap

## Pattern

When a Go monorepo has a layered architecture (main package + internal packages), database migrations may exist in multiple places:

- `db.go` — `func (a *app) migrate()` — method on the main package's app struct, often **dead code**
- `internal/models/models.go` — `func Migrate(ctx context.Context, db *sql.DB)` — the **real** startup migration

The real migration function is discovered by tracing `main()`:

```go
// main.go
import "project/internal/models"

func main() {
    // ...
    models.Migrate(ctx, db)  // ← THIS is the real migration
    models.Seed(ctx, db)     // ← THIS is the real seed
}
```

## Diagnostic

```bash
# Find which migrate function main() actually calls
grep -n "Migrate\|migrate\|Seed\|seed" main.go

# If it imports internal/models → the real function is models.Migrate()
# If it calls a.migrate() → the real function is on the app struct
```

## Verification

After adding schema changes to the real migration function:

```bash
cd apps/backend-go
go build -o /tmp/binary .
strings /tmp/binary | grep "your_new_create_table_literal"
# Must match before deploying
```

## Why It Happens

During initial migration from another stack (Cloudflare/Neon → local Go/SQLite), a developer may stub `app.migrate()` in `db.go` as a quick prototype, then later build the real migration in `internal/models/` without removing the stub. Subsequent patches to `db.go` silently succeed but never take effect because `main()` calls `models.Migrate()`, not `a.migrate()`.
