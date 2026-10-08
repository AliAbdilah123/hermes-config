# Nginx static SPA deployment with a separate API service

Use when Nginx serves a static frontend directory while systemd runs the API independently.

## Discovery

1. Inspect the active systemd unit to identify its working directory, executable, environment file, and API port.
2. Search the active Nginx configuration for the project path, static alias, API proxy, and any dedicated project hostname.
3. Probe candidate public URLs. Prefer the hostname that returns the application HTML over a guessed project slug or path.
4. Read the frontend build configuration and set its public base path only when the Nginx mount actually requires one. A dedicated hostname usually serves at `/`; a shared host may require `/projects/<slug>`.

## Deploy and restart

1. Build with the exact production base path.
2. Publish the complete clean output with `rsync -a --delete build/ <nginx-root>/`; copying individual files can leave incompatible hashed assets behind.
3. Restart the named systemd service when the requested delivery includes a project restart, even if the source change is frontend-only. Do not silently reinterpret “restart the project” as “static files need no restart.”
4. Poll a known local health endpoint until ready, then verify `systemctl is-active` and the process start timestamp/PID.

## Public verification

Verify the canonical public hostname, not only an assumed URL:

- application HTML returns 200;
- API health returns 200 through the public proxy;
- emitted JS/CSS URLs return their correct MIME types rather than SPA fallback HTML;
- a unique marker from the changed component exists in the deployed public bundle;
- browser E2E verifies the rendered interaction when available.

If browser automation is unavailable, report that limitation explicitly. HTTP, MIME, and bundle-marker probes prove deployment integrity but do not replace rendered interaction E2E.

## Pitfalls

- A plausible `dev-<repository-name>` hostname can return a valid but unrelated placeholder response. Discover the configured domain from Nginx and verify the returned HTML.
- A shared-host path may be intentionally blocked by a path guard while the dedicated hostname is canonical.
- Building without the required base path can produce valid files whose asset URLs 404 after deployment.
- Testing a guessed asset filename is brittle. Extract current hashes from deployed HTML or the generated manifest.
