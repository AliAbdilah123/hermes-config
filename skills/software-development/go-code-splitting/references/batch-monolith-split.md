# Batch Go monolith refactor — self-flow, fnb-pos, multitenant-auth

## Goal
Split three large `main.go` files (>2k lines each) into thin entry points + `internal/app` packages, build binaries, and verify with health checks.

## Reference line counts after split

| Project | Before | After (main.go) | After (internal/*) | Total |
|---|---|---|---|---|
| self-flow/packages/api/v1 | 2,279 | 20 | ~2,301 | 2,321 |
| fnb-pos/backend | 2,146 | 27 | ~2,164 | 2,191 |
| multitenant-auth-saas-boilerplate | 2,127 | 30 | ~2,019 | 2,049 |

## Patterns that emerged

### 1. Dynamic handler grouping (fnb-pos)
Instead of one `handlers.go`, classify methods by name prefix and write N files with the same `package app` and freshly detected imports.

```python
# Pseudocode
starts = [i for i, line in enumerate(lines) if re.match(r'^func \(a \*App\) ', line)]
boundaries = [(idx, idx+1) for idx in starts]  # expand to next top-level func
groups = {"handlers_common.go": [...], "handlers_sales.go": [...], ...}
for fname, bounds in groups.items():
    content = extract(bounds)
    imps = detect_imports(content)
    write(f"internal/app/{fname}", f"package app\n\nimport (...)\n\n{content}")
```

### 2. External binary replacement
Existing deployed binaries were found at:
- `/opt/fnb-pos/fnb-pos-server` (root-owned)
- `/usr/local/bin/multitenant-auth-saas-boilerplate-api` (root-owned)

`cp` from the user context failed with `permission denied`. Options:
- `sudo cp <src> <dst>` if the user has sudo
- Build directly to the destination if the directory is user-writable
- Otherwise instruct the user to replace the binary manually

### 3. Runtime ports
Use ephemeral, non-standard ports to avoid conflicting with production services:
- `PORT=8096 ./server` for self-flow
- `ADDR=":19087" go run ./cmd/api` for multitenant-auth
- `PORT=8080 go run ./main.go` for fnb-pos (only if 8080 is confirmed free)

Verify with `curl -s http://127.0.0.1:<port>/api/v1/health`.

## Verification checklist per project
1. `git status` clean before split
2. Split `main.go` into `internal/app/*.go`
3. Rename unexported helpers to exported if `main` calls them
4. Add `SetMigrations(fs embed.FS)` if `migrations/*.sql` moves out of `main.go` package
5. Add missing imports to every new file (gofmt does not add imports)
6. `go build ./cmd/api` or `go build ./main.go`
7. Copy binary to `/tmp/` or build destination
8. Run binary with `PORT/ADDR` and `curl` health endpoint
