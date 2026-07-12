# New local Go + SQLite + Vite project deploy pitfalls

Use when creating a fresh small project from a copied/boilerplate frontend and a new Go API.

## Pitfalls and fixes

### 1. Do not commit copied runtime artifacts

When copying an existing frontend's `node_modules` to avoid reinstalling, create `.gitignore` before the first commit:

```gitignore
frontend/node_modules/
frontend/dist/
frontend/tsconfig.tsbuildinfo
bin/
sqlite.db*
```

If already committed, clean the index and amend:

```bash
git rm -r --cached frontend/node_modules frontend/dist bin sqlite.db sqlite.db-shm sqlite.db-wal frontend/tsconfig.tsbuildinfo || true
git add .gitignore backend frontend/package.json frontend/index.html frontend/src frontend/tsconfig.json frontend/vite.config.ts
git commit --amend --no-edit
```

### 2. Grouped Go struct fields cannot share one JSON tag

This is wrong for API DTOs:

```go
type Workspace struct { ID, Name string `json:"id"` }
```

It serializes both fields with the same tag behavior and commonly drops/renames fields in surprising ways. Use explicit fields:

```go
type Workspace struct {
    ID   string `json:"id"`
    Name string `json:"name"`
}
```

Apply this to request structs too; `Name, Description string `json:"name"`` means `description` cannot decode correctly and `name` may appear missing.

### 3. Check local ports before installing systemd units

Existing project services may already occupy common ports. Before choosing a port:

```bash
for p in 8100 8101 8102 8103 8104 8105; do
  ss -ltn "sport = :$p" | grep -q LISTEN || { echo "$p free"; break; }
done
```

Then set the chosen port in the systemd `Environment=` and nginx `proxy_pass` together.

### 4. Verify with Host header before public DNS/proxy assumptions

For a new nginx domain vhost, verify locally first:

```bash
curl -fsS -H 'Host: app.example.com' http://127.0.0.1/api/health
curl -fsSI -H 'Host: app.example.com' http://127.0.0.1/ | head -n 1
```

Then verify the public domain and bundle marker:

```bash
curl -fsSI http://app.example.com/ | head -n 1
curl -fsS http://app.example.com/assets/<bundle>.js | grep -o 'app-specific marker'
```
