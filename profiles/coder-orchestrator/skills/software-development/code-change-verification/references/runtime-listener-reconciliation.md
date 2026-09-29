# Runtime listener reconciliation

Use before replacing or restarting a deployed service binary when nginx proxies to a fixed local port.

1. Read the exact systemd `ExecStart`, working directory, and env-file argument.
2. Read the effective listener value from that env file without printing unrelated secrets.
3. Read nginx `proxy_pass` for the public route and compare it with the effective listener.
4. Inspect ownership of both the configured and proxied ports (`ss -ltnp`). A previously healthy public route may have been served by a stale process or a different service.
5. Resolve any mismatch before replacing the binary. Preserve the env file as runtime configuration; do not commit secrets.
6. Restart, then poll the effective local health URL. Verify the service PID/start timestamp and the public proxied health route separately.

A restart loop reporting `address already in use` after deployment is a runtime-configuration failure, not application behavior. Stop the loop, identify the port owner, align the service listener with nginx, and require both local and public health before continuing to browser E2E.