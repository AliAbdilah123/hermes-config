# Dashboard frontend build troubleshooting

## Symptom: Dashboard process is listed by `--status` but HTTP port is closed

Root cause: static assets not built. The Hermes dashboard server ships without a bundled `web_dist` in some install states (fresh source install, reinstall, sandboxed environments). It fails silently on startup.

## Reproduction

```bash
hermes dashboard --stop
hermes dashboard --no-open
# check for web_dist: should exist at /home/ubuntu/.hermes/hermes-agent/hermes_cli/web_dist/
ls -la /home/ubuntu/.hermes/hermes-agent/hermes_cli/web_dist/
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9119
# returns 000 or connection refused
```

## Fix

From the web source directory:

```bash
cd /home/ubuntu/.hermes/hermes-agent/web
npm install            # required when node_modules is incomplete or tsc bootstrap is missing
npm run build          # outputs to ../hermes_cli/web_dist/
```

Then restart the dashboard.

## Confirmed command paths on this host

- Explicit start: `cd /home/ubuntu/.hermes && /home/ubuntu/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main dashboard --port 9119 --no-open`
- Build outDir: `vite.config.ts` sets `outDir: "../hermes_cli/web_dist"`, so assets land at `/home/ubuntu/.hermes/hermes-agent/hermes_cli/web_dist/`
- Invalid subcommand: `python -m hermes_cli.main web` — use `dashboard`
- Remote exposure no longer uses `--insecure --host 0.0.0.0`; non-loopback binds now require `dashboard.basic_auth` in `config.yaml`
- External access should be via reverse proxy/tunnel or nginx, not direct public bind

## Why this happens

- The TypeScript/Vite build requires a working `typescript/lib/tsc` bootstrap chain.
- A fresh `npm install` on an already-initiated node_modules warns about engine mismatch but still succeeds functionally — do not treat EBADENGINE as fatal.
- Stale dashboard PIDs from prior runs can make `hermes dashboard --status` look busy while the new process has actually failed.

## Portable build flags

None are required; defaults work. Use `--skip-build` only when dist is confirmed present.
