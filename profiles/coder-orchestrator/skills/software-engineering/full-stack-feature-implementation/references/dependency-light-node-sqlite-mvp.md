# Dependency-light Node/SQLite MVP delivery

Use this pattern for a small, single-process MVP when Node 22+ is available and the acceptance scope does not require a framework.

## Minimal architecture

- Use `node:http` for routing/static delivery, `node:sqlite` for persistence, and `node:crypto` for password hashing, random session/CSRF tokens, and token hashing.
- Keep the UI as static HTML/CSS/ES modules when native forms, dialogs, fetch, and responsive CSS cover the interaction model.
- Use integer minor currency units and database `CHECK`/foreign-key constraints. Validate again at the HTTP trust boundary.
- Store only hashes of opaque session tokens; use `HttpOnly`, `SameSite=Strict`, scoped cookies, finite expiry, and CSRF tokens on mutations.
- Scope every workspace/resource lookup by authenticated owner. Return 404 for cross-owner IDs to avoid disclosure.
- Build can be a deterministic copy from `public/` to `dist/`; do not add a bundler without a concrete need.

## Strict TDD sequence

1. Write parser/domain and HTTP acceptance tests before `src/` exists; run them and require the expected missing-feature RED.
2. Implement the smallest server/schema needed for GREEN.
3. Write static UI contract tests before public assets; run the expected RED, then add the UI.
4. Add browser E2E only after unit/HTTP tests are green. Exercise the real server and temporary database.
5. After every final edit, rebuild, start on a fresh database and free port, rerun E2E, stop the process, then run the canonical test command last.

## Base-path-safe serving

The server should strip a configured mount prefix before route matching and scope its session cookie to that prefix. In a static ES module, derive the browser mount from the module URL rather than hard-coding root requests:

```js
const mount = new URL('./', import.meta.url).pathname.replace(/\/$/, '');
const api = path => fetch(mount + path);
```

This preserves root operation while allowing a subpath mount without build-time injection.

## Browser verification pitfalls

- Wait for asynchronous state boundaries explicitly. After clicking an action that fetches data and opens a dialog, wait for `dialog[open]` before filling fields; a click completion does not mean the async handler finished.
- Scope duplicate labels with stable IDs or dialog/form locators. A hidden authentication `Nama` input and an open workspace `Nama` input make global label queries ambiguous.
- Assert account defaults by visible option text, not a database ID such as `1`; IDs vary with fixtures and prior runs.
- After creating a workspace, select it explicitly before asserting its empty state. UI refresh logic may intentionally preserve the current workspace.
- Use a unique user and fresh temporary database, verify reload persistence and cross-workspace isolation, collect `pageerror`/unexpected console errors, and check mobile horizontal overflow.
- Treat locator/timing defects as harness failures: fix the harness and rerun the complete flow rather than changing product behavior.

## Scope ceiling

This architecture is appropriate for a calm MVP, not automatically for multi-instance production. Add migrations, a mature router/framework, external session storage, connection pooling, or a frontend build pipeline only when deployment topology or measured complexity requires them.
