# Dashboard frontend build troubleshooting

## Symptom: Dashboard process is listed by `--status` but HTTP port is closed

Root cause: static assets not built. The Hermes dashboard server ships without a bundled `web/dist` in some install states (fresh source install, reinstall, sandboxed environments). It fails silently on startup.

## Reproduction

```bash
hermes dashboard --stop
hermes dashboard --host 0.0.0.0 --insecure --no-open
# check for dist: should exist at /path/to/hermes-agent/web/dist or hermes_cli/web_dist
ls -la /path/to/hermes-agent/web/dist
curl -s -o /dev/null -w "%{http_code}" http://localhost:9119
# returns 000 or connection refused
```

## Fix

From the Hermes source home (`~/.hermes/hermes-agent` inside the venv-managed install):

```bash
cd /home/ubuntu/.hermes/hermes-agent/web
npm install            # required when node_modules is incomplete or tsc bootstrap is missing
npm run build          # outputs to ../hermes_cli/web_dist/
```

Then restart the dashboard.

## Why this happens

- The TypeScript/Vite build requires a working `typescript/lib/tsc` bootstrap chain.
- A fresh `npm install` on an already-initialized `node_modules` warns about engine mismatch (`@icons-pack/react-simple-icons` wants Node >=24) but still succeeds functionally — do not treat EBADENGINE as fatal.
- Stale dashboard PIDs from prior runs can make `hermes dashboard --status` look busy while the new process has actually failed.

## Portable build flags

None are required; defaults work. Use `--skip-build` only when `dist` is confirmed present.
