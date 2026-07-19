# Systemd Workspace Root vs Project Directory Containment

Use this when a service rejects a valid project path with an error such as `project directory must be inside workspace root`.

## Diagnosis

1. Find the validation error in source and identify how the allowed root is selected.
2. Trace the running entry point. A common fallback is `os.Getwd()`, which under systemd resolves to the unit's `WorkingDirectory=`.
3. Inspect the effective unit and process environment:

```bash
systemctl cat <service>
systemctl show <service> -p Environment --value
pid=$(systemctl show <service> -p MainPID --value)
tr '\0' '\n' < /proc/$pid/environ | grep '^WORKSPACE_ROOT='
```

4. Canonicalize both paths with `readlink -f`. A sibling project is outside an app-local working directory even when both live under the same parent.

## Minimal fix

If the product intentionally manages sibling projects, configure the existing root override rather than weakening or deleting containment validation:

```ini
# /etc/systemd/system/<service>.service.d/workspace-root.conf
[Service]
Environment=WORKSPACE_ROOT=/home/ubuntu/projects
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl restart <service>
systemctl is-active <service>
```

Containment remains a security boundary: select the narrowest common parent that covers intended projects. Do not set `/`, `/home`, or disable canonical-path checks merely to accept one directory.

## Verification

- Confirm the variable appears in `/proc/<pid>/environ`, not only in the unit file.
- Confirm the target directory exists and canonicalizes beneath the configured root.
- Exercise the exact create-project request when credentials are available; otherwise run the targeted containment/API regression test and verify local/public service health.
- A config-only service fix normally has no repository diff to commit. Do not create an empty commit.
