# Plan gates and Go + Vite production delivery

## Authorization when a plan says “planning only”

A planning artifact may correctly state that it does not itself authorize code or deployment. A later direct user instruction such as “implement this” is the separate authorization that gate requires. Use the plan as scope and acceptance criteria; use the current user message to determine authorization. If the current request only asks to review, explain, or revise the plan, leave code and production untouched.

## Compiled Go API + nginx-served Vite SPA

Prove each boundary independently:

1. Inspect `systemctl cat <service>` for the exact `ExecStart`, `WorkingDirectory`, and environment file. Do not assume production executes a binary in the repository.
2. Build the API and install it at the discovered `ExecStart` path.
3. Build the SPA and deploy `dist/` with deletion to the exact nginx document root so stale hashed assets do not linger.
4. Restart the service and poll its real local health endpoint with a bounded retry. An initial refusal followed by health is a startup readiness race, not deployment failure.
5. Compare the public HTML asset hash with `dist/index.html`; probe referenced JS/CSS MIME types.
6. Exercise the new state transition in an authenticated browser on the exact public route. Tests, service health, matching assets, and HTTP 200 are supporting evidence, not substitutes.

Status stays **VERIFYING** while browser E2E is actively running or its runtime is being repaired. If work stops before authenticated E2E passes, report **STOPPED**, never READY.
