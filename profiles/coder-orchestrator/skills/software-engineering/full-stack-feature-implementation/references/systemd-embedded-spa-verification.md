# systemd + embedded SPA deployment verification

Use when a backend executable embeds generated frontend assets.

1. Read the active unit and drop-ins; identify the exact `ExecStart` binary path.
2. Run frontend tests and production build, confirming the generated asset names.
3. Run backend tests and build directly to the `ExecStart` path (or atomically copy the verified binary there).
4. Restart the service and confirm it is active.
5. Retry the local readiness request a small bounded number of times; an immediate connection refusal during startup is not a deployment verdict.
6. Fetch live HTML from the service and compare its JS/CSS asset hash names with the just-built output.
7. Check the working tree, then commit and push when the user's workflow requires it.

Minimal shell shape:

```sh
systemctl cat APP.service
npm test -- --run && npm run build
go test ./... && go build -o /path/from/ExecStart ./cmd/APP
sudo systemctl restart APP
for i in 1 2 3 4 5; do curl -fsS http://127.0.0.1:PORT/ > /tmp/APP-index && break; sleep 1; done
systemctl is-active APP
grep -o 'index-[A-Za-z0-9_-]*\\.js' /tmp/APP-index
```

Pitfall: building a second binary in the repository root does not deploy a service whose unit runs `bin/APP`. A green restart only proves that some executable started, not that the new embedded assets are live.