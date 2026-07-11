---
name: go-code-splitting
description: Split Go files and reorganize logic into focused packages while keeping the same binary buildable.
---

# Go Source File Splitting

Use when a Go `main.go` or handler file exceeds ~500–800 lines and needs to be decomposed into focused files/packages without changing module structure, vendored paths, or database schema.

## Core Constraint

Stay inside the declared Go module. Write split files under the module root's existing `internal/<domain>/` tree (e.g., `backend/internal/app/`), not under `cmd/<binary>/internal/`. The `internal` directory is only visible to packages within the same module.

## Step-by-step

1. Start from a clean state. If `git status` shows working-tree changes, `git checkout -- <file>` first so line numbers in the original match the actual file.
2. Discover top-level declarations with exact ranges. Use regex `^(\s*)(func |var |type |const )` at indent 0 to find boundaries; avoid `grep` alone because it misses start lines and under-reports end lines.
3. Build one target file per responsibility. Write a verification script if there are many pieces; otherwise hand-audit counts with `wc -l`.
4. **Export only what `main` needs.** Anything called from `main` must be exported (`Routes`, `LoadConfig`, `Migrate`, `SeedSuperAdmin`, `SetMigrations`).
5. Update `main.go` to import the new package path, call exported functions, and delegate the rest.
6. `go build ./...` after every small change. Stop on the first error, fix it, re-run.
7. Run the binary on a random port with `ADDR=:<high_port>` and `curl` the health endpoint. Do not skip runtime verification — build success does not guarantee `http.Server` boots or call paths are wired correctly.

## Pitfalls

### embed.FS paths are relative to the declaring package
If `migrations/*.sql` lives next to `main.go`, splitting migrations into `internal/app/migrations.go` breaks `embed.ReadDir("migrations")` because the FS path becomes relative to `internal/app/`, not the project root.

**Fix**: keep the `//go:embed migrations/*.sql` declaration in `main.go`, and add a setter in `internal/app`:

```go
var migrations embed.FS
func SetMigrations(fs embed.FS) { migrations = fs }
```

In `main()` before `app.Migrate()`:
```go
app.SetMigrations(migrations)
```

### Package-qualified types vs same-package references
Once a type is extracted into a new package, all files in that package must refer to it unqualified (`Config`, `App`), while files outside must use `pkg.Config`. Be consistent: either keep `Config` in the same package as `App` or update every call site.

### Duplicate helpers after idempotent extraction
When stripping helpers from the original file, remove duplicates that got copied into multiple new files. Same top-level packages cannot redeclare identifiers. If a helper was already in `helpers.go`, delete it from `handlers_delegation.go`.

### Forgetting imports in new packages
Each new file needs its own `import` block. Common misses: `context`, `sql`, `strings`, `errors`, `encoding/json`, `fmt`, `time`, `net/http`. Run `gofmt` to catch formatting issues, but do not rely on it to add missing imports.

### Binary name confusion after split
`go build ./cmd/api` writes the binary to `./cmd/api` (a directory on Linux), not an executable file. Always use `go build -o /tmp/<name> ./cmd/api` or run the binary from the project root with explicit path.

## Choosing Cut Lines

Route all domain handlers (`auth`, `tenants`, `notifications`, `catalog`, `delegation`, `webhooks`) into separate `handlers_*.go` files. Group shared helpers and types into `helpers.go` and `types.go`. Route config/env loading to `config.go`. Keep middleware (`jsonHandler`, `cors`, `requestLog`) with the routes definition unless it exceeds ~30 lines.

## References

- See `references/delegate-backend.md` for the concrete `delegate` backend refactor that informed these rules.