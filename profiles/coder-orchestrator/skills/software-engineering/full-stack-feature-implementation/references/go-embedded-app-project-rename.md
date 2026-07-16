# Renaming a deployed Go app with an embedded Vite frontend

Use when one Go process serves both the API and an embedded Vite build, while nginx proxies the entire project subpath to that process.

## Identify this deployment shape

Before applying a static-SPA rename recipe, verify:

- Go uses `//go:embed` for the frontend build.
- The service executes one Go binary.
- nginx proxies `/projects/<slug>/` wholesale to localhost rather than serving `/var/www/html/projects/<slug>/`.
- Vite's `base` is compiled into the embedded HTML/assets.

A successful `curl` of HTML and assets does not prove post-auth rendering works. Reproduce a fresh-account API sequence and inspect collection shapes used by the first authenticated render.

## Safe rename sequence

1. Add a regression test for the reported bug before combining it with identity changes.
2. Update source identity: product labels, Go module/imports, command directory, output binary, Vite base, tests, docs, and config references.
3. Build Vite first, then copy/sync `dist` into the directory covered by `//go:embed`.
4. Build the Go binary after the embedded files are current; otherwise the executable still contains the old frontend.
5. Stop the service before moving the project directory or a live SQLite database. Keep the DB, `-wal`, and `-shm` files together.
6. Install the renamed systemd unit with the new `WorkingDirectory` and `ExecStart`.
7. Replace the nginx include/location with the new slug while preserving an explicit old-slug redirect when compatibility is wanted.
8. Validate nginx, start the renamed service, and verify direct-port plus proxied HTML, API, and referenced assets.
9. Run a real fresh-account browser/API smoke against the new public path; HTTP 200 alone is insufficient for SPA runtime verification.
10. Search source, systemd, and nginx for stale old absolute paths. Intentional redirect references are the only expected leftovers.

## Empty-state blank-screen check

Fresh accounts often expose API contracts hidden by populated accounts. In Go, nested nil slices serialize as `null`:

```go
lane := Lane{Jobs: []Job{}}
```

Initialize nested collection fields before scanning/appending, and assert raw JSON contains arrays (`[]`) rather than `null` when the frontend calls `.map()`, `.filter()`, or `.length` immediately after authentication.

## Pitfalls

- Do not deploy only `frontend/dist`; the running binary will continue serving the previously embedded files until rebuilt and restarted.
- Do not assume the generic static directory exists or matters when nginx proxies the whole app.
- Do not rename/move an open SQLite main file without its WAL/SHM sidecars.
- Do not remove the old unit or route until the new service, new assets, API, and fresh-account render all pass.
- Keep the bug fix and broad rename separately testable even if delivered in one final commit.
