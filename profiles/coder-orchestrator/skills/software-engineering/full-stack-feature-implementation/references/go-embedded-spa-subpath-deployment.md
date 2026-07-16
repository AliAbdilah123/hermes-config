# Go embedded SPA deployment under an nginx subpath

Use this when a Go `net/http` service embeds a Vite SPA and nginx exposes it at `/projects/<slug>/`.

## Build and browser paths

- Set Vite `base` to the public subpath, including trailing slash:
  ```ts
  export default defineConfig({ base: '/projects/<slug>/' })
  ```
- Derive API and SSE URLs from `import.meta.env.BASE_URL`; host-root `/api` paths bypass the nginx subpath:
  ```ts
  const base = import.meta.env.BASE_URL
  fetch(base + 'api/auth/me')
  new EventSource(base + 'api/jobs/1/stream')
  ```
- Build first, then copy `dist/*` into the Go embed directory before compiling the Go binary. Confirm public HTML references subpath-prefixed asset URLs and fetch the referenced JS/CSS directly.

## Service and nginx

- Check the chosen backend port with `ss` before creating the unit. A successful build says nothing about port availability.
- For user-installed CLIs, systemd often lacks the interactive shell PATH. Set an explicit, non-secret PATH containing the user's CLI directory, e.g. `/home/ubuntu/.local/bin`, plus standard system paths. Verify CLI availability through the running service's API, not the login shell.
- For SSE, disable nginx proxy buffering on the app location.
- A minimal proxy shape:
  ```nginx
  location = /projects/<slug> { return 301 /projects/<slug>/; }
  location ^~ /projects/<slug>/ {
      proxy_pass http://127.0.0.1:<port>/;
      proxy_http_version 1.1;
      proxy_buffering off;
      proxy_set_header X-Forwarded-Proto $scheme;
  }
  ```
- Run `nginx -t`, restart/enable the service, reload nginx, and require `systemctl is-active` plus direct-backend and public-path HTTP 200 checks.

## Scheduler test race

If the app starts its scheduler in `Open()`, API tests that create a queued job can race the scheduler before asserting edit/state rules. Make the fixture deterministic by pausing its lane before job creation (or inject a disabled scheduler in tests). Do not weaken production scheduling merely to stabilize the test.

## Verification checklist

1. Frontend tests and production build.
2. Backend tests and production build.
3. Service active after a short restart window (not merely `activating`).
4. Public index and every referenced asset return 200.
5. Authenticated API smoke through the nginx subpath.
6. Runtime CLI/readiness endpoint reflects the service environment.
7. Commit; push only when a remote exists, and report a missing remote plainly.
