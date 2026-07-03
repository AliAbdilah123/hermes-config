# Go Single-File API Routing Pitfalls

Collected from building single-file Go + SQLite APIs. These hit every time.

## 1. Switch-case routing MUST `return` after each handler

Without `return`, execution falls through to the auth middleware block, which tries to
extract a token from the already-written response. The result: a 401 error JSON gets
appended to a 200 login response body, making both unparseable.

```go
// BROKEN — falls through to requireAuth after handler writes response
switch {
case method == "POST" && slug == "auth/login":
    a.login(w, r)   // writes 200 JSON, then...
case method == "GET" && slug == "health":
    a.ok(w, ...)    // writes 200 JSON, then...
}
// Falls through here → requireAuth writes 401 on top of the 200
user := a.requireAuth(w, r)

// FIXED
switch {
case method == "POST" && slug == "auth/login":
    a.login(w, r)
    return   // ← mandatory
case method == "GET" && slug == "health":
    a.ok(w, ...)
    return   // ← mandatory
}
```

This is easy to miss because Go switch does NOT have implicit fallthrough (unlike C).
The issue is the code after the switch, not inside it.

## 2. Path trimming needs both `/prefix` and `prefix` variants

When using `mux.HandleFunc("/api/v1/", handler)` alongside
`mux.HandleFunc("/projects/slug/api/v1/", handler)`, Go's default mux strips the
registered prefix before calling the handler. The incoming path in the handler may
or may not have the leading `/` depending on the mux registration.

```go
// SAFE — handles both with and without leading slash
path := strings.TrimPrefix(r.URL.Path, "/projects/slug")  // project-specific prefix
path = strings.TrimPrefix(path, "/api/v1")                 // with leading /
path = strings.TrimPrefix(path, "api/v1")                  // without leading /
path = strings.TrimPrefix(path, "/")                       // final cleanup
```

Without the second `TrimPrefix("api/v1")`, paths registered via mux without the
project prefix will still have the `/api/v1` intact after the first trim.

## 3. modernc.org/sqlite "out of memory (14)" = file permission error

When using `modernc.org/sqlite` (pure-Go SQLite, no CGO), a file permission error
on the database path produces the misleading error:

```
unable to open database file: out of memory (14)
```

This means the process cannot write to the directory containing the DB file.
Fix: `chown` the data directory to the user running the service.

```bash
# systemd service running as user 'ubuntu'
sudo mkdir -p /var/lib/myapp
sudo chown -R ubuntu:ubuntu /var/lib/myapp
sudo systemctl restart myapp
```

## 4. bcrypt hash stored as `string(ph)` — not `[]byte` directly

```go
ph, _ := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
// ph is []byte — cast to string for SQLite TEXT column
db.Exec("INSERT INTO users (password_hash) VALUES (?)", string(ph))

// Later: compare against the stored string
bcrypt.CompareHashAndPassword([]byte(storedHash), []byte(inputPassword))
```
