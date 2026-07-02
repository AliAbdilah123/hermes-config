# Go Build Cache — Stale Binary After Source Changes

## Symptom

You modify Go source files, `go build` succeeds, deploy the binary, but the running service does NOT reflect your changes. API responses, log messages, or schema migrations are missing. The binary was built from cached objects that predate your edits.

## Root Cause

`go build` caches compiled packages aggressively. When only one file in a package changes, Go may reuse cached `.a` files for the other files, and sometimes the new compilation doesn't incorporate all changes — especially after `patch` tool edits that don't update file modification timestamps reliably, or when `go build` was invoked once before the edits and the cache already holds the old version.

## Diagnostic

```bash
# Check if the expected string literal exists in the binary
strings /path/to/binary | grep "expected_literal_from_your_change"
# No output → binary is stale
```

Use a unique, long-enough substring from your change — a new SQL statement, a new log message, a function name.

## Fix

```bash
# Clean the build cache, then rebuild
cd /path/to/package
go clean -cache
CGO_ENABLED=1 go build -o /path/to/binary .

# Verify
strings /path/to/binary | grep "expected_literal"
```

## Prevention

- After any source change that must appear in the binary, verify with `strings | grep`.
- In CI, `go clean -cache` before building; the cache is for local iteration speed.
- `gofmt -w` the file before building — touching the file ensures Go sees it as modified.

## Cross-check: deployment path

A related pitfall: the binary builds correctly but deploys to the wrong path (`systemctl cat service | grep ExecStart` reveals the actual path). A stale-binary symptom can actually be a wrong-path symptom. Check both.

## Dead-code variant: source compiled but function never called

Your changes ARE in the binary (confirmed by `strings | grep`) but the running service still doesn't reflect them. The function you patched was compiled into the binary but is **dead code** — the real startup path calls a different function with a similar name in a different package.

**This is common in Go monorepos with layered architectures** where:
- `db.go` has `func (a *app) migrate()` — a method on the main package's `app` struct
- `internal/models/models.go` has `func Migrate(ctx, ...)` — the package-level function actually called from `main()`

**Diagnostic:**

```bash
# 1. Verify the binary DOES contain your change
strings /path/to/binary | grep "your_new_table_or_literal"
# Output found → not a cache issue

# 2. Check if the changed function is called anywhere
cd project/backend
grep -rn "func_name" --include="*.go"
# If only defined in one file and never referenced elsewhere → dead code

# 3. Trace the actual startup chain from main()
grep -rn "Migrate\|migrate\|Seed\|seed" main.go
# Find which package's function is actually called
```

**Fix:** Find the real function that runs on startup (usually in `internal/models/` or `internal/db/`) and apply your changes there instead. Verify the real function is on the call chain by grepping `main()` for its import and invocation.
