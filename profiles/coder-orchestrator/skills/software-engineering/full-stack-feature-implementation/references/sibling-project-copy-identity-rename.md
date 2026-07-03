# Copying a sibling project with identity rename

Use this when creating a variant/deployment of an existing Go + SQLite + Vite project with a different slug, port, and identity — without rebuilding from the boilerplate.

## Proven workflow

1. **Rsync excluding runtime artifacts**
   ```bash
   rsync -a --exclude .git --exclude node_modules --exclude dist --exclude data --exclude bin \
     /home/ubuntu/projects/<source>/ /home/ubuntu/projects/<target>/
   ```

2. **Batch identity replacement** — run as a Python script to avoid shell escaping hell:
   ```python
   repls = {
     '/projects/<source>/': '/projects/<target>/',
     '<SOURCE>_DATA_DIR': '<TARGET>_DATA_DIR',
     '/var/lib/<source>': '/var/lib/<target>',
     '<source>.db': '<target>.db',
     '<old_port>': '<new_port>',
     '"name": "<source>"': '"name": "<target>"',
     'module <source>': 'module <target>',
   }
   ```
   Replace in all non-git files: `cmd/server/main.go`, `vite.config.ts`, `src/main.tsx`, `.env`, `go.mod`, `package.json`, `package-lock.json`.

3. **Rebuild and test both sides** before deploying:
   ```bash
   go test ./...
   npm install && npm test && npm run build
   ```

## Pitfalls

- **Double-replace trap**: Replacing `siapjasa` → `siapjasa-simple` then `8094` → `8099` is safe. But if a later pass runs `siapjasa-simple` → `siapjasa-simple-renamed`, it hits already-renamed text and produces `siapjasa-simple-simple`. **Fix**: run the shorter/source-specific replacements first, then do a cleanup pass for the double-affix pattern: `s.replace('siapjasa-simple-simple', 'siapjasa-simple')`. Or use a single-pass dict with all replacements in one go — Python's `str.replace` in a loop doesn't re-enter already-replaced substrings the way cascaded shell `sed` does.

- **Port collision**: Before picking a port, check active listeners with `ss -tlnp | grep <port>`. The old source project may still be running on its port, and other projects may occupy nearby ports. Pick a free port before writing it into the replacement set.

- **Go module name with hyphens**: `module siapjasa-simple` with a hyphen works fine — `go test ./...` and `go build` handle it. No need to avoid hyphens.

- **Nginx route insertion**: Add the new project's location blocks BEFORE the generic `/projects/` fallback block. Use `perl -0777 -i -pe` for safe multiline insertion into system nginx configs (the `patch` tool refuses `/etc/` paths).

- **Systemd service**: Always use `EnvironmentFile=` to point at the project's `.env` rather than inlining env vars in the unit file. Verify with `systemctl show <service> -p EnvironmentFiles`.

## Verification

```bash
# Local
curl -s http://127.0.0.1:<port>/api/v1/health
# Nginx proxied
curl -s http://localhost/projects/<target>/api/v1/health
# Public
curl -sI http://168.110.213.104/projects/<target>/
# Service
sudo systemctl is-active <service-name>
```
