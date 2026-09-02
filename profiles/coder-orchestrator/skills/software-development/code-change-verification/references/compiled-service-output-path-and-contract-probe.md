# Compiled Service Output Path and Contract Probe

Use when deploying a compiled service whose source checkout contains nested package/module directories and systemd runs a separately located binary.

## Failure pattern

A build succeeds and the service restart succeeds, but production still returns the old behavior. A common cause is resolving a relative `-o` path from the wrong working directory. For example, running from `<repo>/backend` with `-o backend/bin/app` creates `<repo>/backend/backend/bin/app`, while systemd continues executing `<repo>/backend/bin/app`.

## Safe sequence

1. Read the effective `ExecStart` from `systemctl show <unit> -p ExecStart`.
2. Resolve the build output to that exact absolute path, or build a sibling `.new` file beside it and atomically rename it into place.
3. Before restart, inspect the built binary for a stable marker from the change when practical (`strings <binary>`), and compare its path/inode or checksum with the intended deployment target.
4. Restart the unit and poll its local health endpoint. A lifecycle-active state alone is insufficient.
5. Exercise the exact changed contract through the public route. For request-routing fixes, send the same query/body shape used by the frontend and assert both response and persisted reload.
6. If public behavior is still old, inspect the response body before editing source again. A repeated old error string strongly suggests stale runtime artifact or wrong proxy/upstream, not a failed source hypothesis.
7. Remove accidental nested build-output directories only after proving they were created by the current build; never clean unrelated workspace files.

## Fixture note

When creation endpoints have unrelated validation or schema constraints, set up the minimum authenticated fixture directly in the runtime database only as prerequisite setup. The browser/public API must still perform the mutation under test, and cleanup plus `PRAGMA integrity_check` must pass afterward.
