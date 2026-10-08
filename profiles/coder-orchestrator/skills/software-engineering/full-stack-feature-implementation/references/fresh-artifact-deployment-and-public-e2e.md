# Fresh artifact deployment and public E2E

Use this when a repository contains generated binaries/build directories and production is served by systemd + nginx or a similar split backend/static setup.

## Deployment sequence

1. Run source-level checks first (backend tests, frontend tests, type checks, production build).
2. **Build the backend binary immediately before installation.** Never assume a checked-in or untracked generated binary matches current source merely because tests passed.
3. Install that fresh temporary binary, sync the fresh static build with deletion enabled, then restart the service.
4. Poll the local health endpoint after restart. `systemctl is-active` alone is insufficient because a service may be inside an auto-restart loop.
5. If startup rejects configuration, inspect logs, rebuild from current source, reinstall, restart, and recheck health. Preserve the durable rule (fresh build plus health poll), not a transient setting name.
6. Verify deployed frontend assets contain a feature-specific marker when practical.
7. Run authenticated E2E against the public domain, exercising the real mutation and reading back persisted state. A direct HTTP/API flow is acceptable when browser automation is unavailable, provided it traverses the public proxy/domain and verifies both status and resulting data.
8. Confirm local HEAD equals remote branch SHA. Report app URL, commit, push, deployment health, and E2E evidence.

## Safe authenticated API probe

- Create an isolated disposable account with a unique email.
- Store cookies in a temporary directory and clean it with a trap.
- Parse the CSRF token without printing it.
- Create minimal disposable records, call the mutation through the public hostname, then read back exact persisted state.
- Print only non-secret evidence: status, disposable record IDs, and expected result fields.

## Pitfalls

- Installing a stale generated binary can regress startup even when current source compiles and tests pass.
- A successful static sync does not prove the backend deployed.
- `active` immediately after restart does not prove readiness; require a successful health response.
- Source/build/push is not delivery. READY requires live deployment plus public E2E.
