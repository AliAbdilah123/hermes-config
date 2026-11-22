# systemd binary release and readiness

Use when a compiled service is deployed through systemd.

1. Inspect the unit's effective `WorkingDirectory`, `EnvironmentFile`, and especially `ExecStart`; do not assume a successful local build replaced the executable systemd runs.
2. Build directly to the `ExecStart` path (or atomically install the artifact there), then restart the service.
3. `systemctl is-active` only proves process state. Readiness may lag briefly after restart, so probe the configured local listen address and retry for a bounded period instead of issuing one immediate request.
4. Verify the changed behavior locally first, then through the public URL. For embedded static assets, probe both the HTML marker and the versioned JS/CSS behavior marker.
5. Confirm the deployed process logs show the expected listen address and no restart loop.

Minimal evidence:

```sh
systemctl cat SERVICE
# build/install to the exact ExecStart path
systemctl restart SERVICE
systemctl is-active SERVICE
# bounded local readiness probe, then public behavior probes
```

Pitfall: building an executable in the repository root while `ExecStart` points to `bin/<name>` leaves the live service on the old artifact even though restart succeeds.