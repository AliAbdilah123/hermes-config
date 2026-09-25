# Static shell / backend runtime audit

Use when a deployed SPA or static frontend returns HTTP 200 but users report that the application does not work.

## Diagnostic sequence

1. Probe the public frontend route and the public API health route independently. A shell `200` does not imply a working application.
2. Read the reverse-proxy mapping to identify the backend host/port and static asset root.
3. Check whether anything listens on the upstream port, then inspect the service manager status and recent journal entries.
4. Trace the startup error into application code and configuration. Distinguish a deployment outage from a compile/test failure.
5. Inspect only aggregate database state needed to validate the startup contract; do not expose secrets or user data.
6. Look for bootstrap cycles: for example, startup requires an existing database user, while creating that user requires the API to start.
7. Run repository tests/builds separately. Passing checks prove module health, not deployed availability.
8. Classify status conservatively: if authenticated public E2E cannot run, report STOPPED or BLOCKED—not READY.

## Report pattern

Explain both the intended flow and the actual stop point. Lead with the runtime boundary:

- static shell status;
- API status;
- upstream service status;
- confirmed startup error;
- source path that turns the error into process exit;
- minimum safe recovery order.

A useful recovery order is: decouple optional integrations from core startup, perform an explicit auditable bootstrap, make capability flags reflect runtime readiness, then require authenticated public E2E.

## Pitfalls

- Do not describe a visible login page as a working login flow.
- Do not conflate HTTP 200 for generated HTML with application availability.
- Do not “fix” bootstrap cycles by silently inserting privileged users or credentials.
- Do not weaken startup validation globally when only an optional integration should degrade gracefully.
- Never include environment values or tokens in the report; presence/absence is enough.
