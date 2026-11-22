# Restart readiness and public E2E targets

## Service restart readiness

`systemctl is-active` only proves the process is running; it does not prove the listening socket or application is ready. After restart:

1. Poll the local health endpoint with a bounded retry loop.
2. Require a successful application-level response before checking the public endpoint.
3. Then run public E2E.

A first connection refusal immediately after an active status is a readiness race, not evidence of a broken deployment. Diagnose only if the bounded readiness check expires.

## Public E2E URL selection

Treat the project's current deployment metadata as authoritative. Before running a checked-in public E2E script, inspect whether its default URL still matches the project's declared public URL. If not, pass the current URL through the script's supported environment variable rather than silently testing an old route.

## Scope failures accurately

A broad public suite may fail after the changed flow already passed because unrelated fixtures or labels drifted. Report all three separately:

- changed-flow result;
- suite stopping point and exact mismatch;
- whether the mismatch touches the edited behavior.

Do not call the complete public suite passed when only the changed-flow case passed. Either repair the stale assertion when in scope or explicitly record the partial verification and blocker.