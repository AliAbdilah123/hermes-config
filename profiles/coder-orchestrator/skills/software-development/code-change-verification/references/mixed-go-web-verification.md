# Mixed Go + Web Workspace Verification

Use when a repository combines a Go service and a pnpm frontend.

First inspect the repository's canonical verifier (`make check`, package script, or equivalent). Run it once from the final workspace state when available; separate parallel test/typecheck/build calls may not satisfy automated verification tracking. Any later source edit invalidates that evidence, so rerun the canonical command before completion.

Only when no canonical verifier exists or it is genuinely unusable, create the verifier with `mktemp /tmp/hermes-verify-<project>-XXXXXX`, write a fail-fast script, execute it against the final workspace, preserve its exit status, and remove it afterward.

```sh
#!/bin/sh
set -eu
cd /absolute/project/path

gofmt -w <changed-go-files>
go test ./path/to/package -run '<focused-behaviors>' -count=1
go test ./...
go vet ./...
go build -o /tmp/<project>-server ./cmd/server

cd apps/web
pnpm test -- --run
pnpm typecheck
pnpm build
```

Notes:
- The focused command proves the changed behavior; the full commands detect regressions.
- Use `-count=1` for focused Go evidence so cache hits cannot mask the current behavior.
- Include generated-output or formatting commands only when they are expected project operations.
- Report this as **ad-hoc verification**, not as a detected canonical suite.
- Do not claim verification from earlier independent runs after subsequent edits; rerun the temporary verifier from the final state.

## Pin frontend behavior in the Go test gate (no browser needed)

When the repo serves frontend assets (`index.html`, JS/CSS) from the Go service, assert *behavioral markers* from a Go integration test instead of relying on a browser. The `httptest.Server` already serves static assets, so fetch them and assert the markers that encode the behavior:

```go
res, err := http.Get(srv.URL + "/orchestrator-v1.js")
// ...read body...
for _, marker := range []string{"IntersectionObserver", "typing-dots", "Retry", "starts when you send"} {
    if !bytes.Contains(js, []byte(marker)) { t.Fatalf("frontend missing %q", marker) }
}
```

Choose markers that name *behavior*, not implementation: `IntersectionObserver` (infinite scroll), a state-label string, a `Retry` affordance. This makes the frontend behavior a first-class part of `go test ./...`, so the same gate that protects the API also protects the UI contract — and it survives CORS/browser-daemon unavailability.

## Public E2E against Cloudflare-fronted endpoints: use curl, not urllib/requests

For live POST/GET E2E against a domain fronted by Cloudflare, scripted `urllib`/`requests` requests can be rejected `403` (bot challenge / non-browser user-agent). `curl` (even via `subprocess`) passed where `urllib` 403'd. Shell out to curl with `-fsS -H 'Content-Type: application/json' --data '<json>'` and parse the JSON reply:

```sh
curl -fsS https://DOMAIN/api/conversations \
  -H 'Content-Type: application/json' \
  --data '{"project_slug":"x","message":"test"}'
```

Wrap the `curl`-driven E2E in a script that asserts the full contract (independent thread created, search finds both, restore returns expected message count, session ID reused). Report the exact IDs/statuses as verifiable evidence — not "uploaded successfully".

## Before (re)implementing: check for work that already landed

Between planning reads and implementation, another actor (a previous turn, a teammate, a queued job) may already have committed the change. Run `git log --oneline -5`, `git status --short --branch`, and `git show --stat HEAD` *before* writing code so you extend/completed the landed work rather than duplicating it (the session found `feat: add searchable chat history` already on `master` and only had to fill the remaining gaps: draft label, typing indicator, retry, infinite scroll).
