# Mixed Go + Web Workspace Verification

Use when a repository combines a Go service and a pnpm frontend but no canonical verifier is detected.

Create the verifier with `mktemp /tmp/hermes-verify-<project>-XXXXXX`, write a fail-fast script, execute it against the final workspace, preserve its exit status, and remove it afterward.

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
