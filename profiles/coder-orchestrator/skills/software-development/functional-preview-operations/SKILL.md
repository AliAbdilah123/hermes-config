---
name: functional-preview-operations
description: Publish and maintain isolated, data-backed web application previews that remain usable for authentication, API calls, and review throughout the approval cycle.
version: 1.0.0
metadata:
  hermes:
    tags: [preview, spa, api, systemd, nginx, verification]
---

# Functional Preview Operations

## Use when

Use for review-stage web previews that require a frontend plus authentication, API data, writes, or other backend behavior. This complements project-specific preview-first and deployment skills.

## Durable runtime rule

A review URL must not depend on a chat-owned background process. If the preview needs an API, run it as a named restartable service—normally a dedicated systemd unit—with:

- a unique localhost port;
- the feature worktree as `WorkingDirectory`;
- an isolated preview database and uploads path;
- explicit preview-aware frontend/callback URLs;
- restart policy and startup at boot where previews are expected to remain reviewable.

A transient process is acceptable only during local diagnosis, never as the final shared preview runtime.

## Workflow

1. Build from a clean feature commit/worktree.
2. Create the preview database using SQLite `.backup` or `VACUUM INTO`; run `PRAGMA integrity_check` and check required auth/program records.
3. Build the frontend for the exact preview basename and API prefix.
4. Install/start the dedicated preview API service and verify its socket plus local health endpoint.
5. Configure an explicit web-server route for both preview assets and preview API proxy; place the specific `/previews/<slug>/api/...` proxy before the broader SPA alias/fallback so API requests cannot return `index.html`. Test configuration before reload, then prove the exact preview API URL returns JSON with the expected content type.
6. Verify the public health endpoint, unauthenticated data endpoint, login/session round trip, authenticated workspace/data route, deep-link SPA fallback, and JS/CSS MIME types. Use a real preview-safe account or sign-up flow; a rendered login form is not authentication evidence. Inspect the frontend auth client before automation: if it restores identity from local storage as well as cookies, seed the token and serialized user under the exact keys and shape used by the application, or use the real sign-in flow. A valid server cookie or plausible guessed storage keys may still redirect to sign-in without issuing a session request. For notification work, generate a representative event in the isolated database, verify its rendered body and relative time, assert raw machine timestamp fragments such as RFC3339 `T...Z` are absent when human-readable copy is required, click the item, and assert the exact resulting pathname. When asserting that an error label such as `Invalid Date` is absent, keep that literal out of fixture titles/bodies; otherwise whole-page text checks produce false failures. Inspect the API payload before changing frontend date formatting: unread/new records often differ through nullable fields such as `read_at`, and a Go `rows.Scan` error on an earlier SQL `NULL` can leave a later timestamp destination empty. Normalize nullable columns with `COALESCE` or `sql.NullString`, check scan errors, and include a regression fixture combining the nullable states. See `references/nullable-row-scan-notification-time.md` for the compact diagnosis, regression, and production-proof recipe.
7. Keep executing the verification chain continuously until complete or concretely blocked. Do not repeatedly report “still working,” “next I will,” or imply background activity when no process is running. If interrupted, state exactly what is complete, what is not, and whether anything is currently executing; then resume immediately when asked.
8. Recheck service activity immediately before sending the URL. Recheck it after any gateway restart or long review delay. If the runtime was started through a chat-owned background process, replace it with the durable service before sharing—even if the process is currently healthy.
8. Record production asset identity before and after to prove isolation.

## Served-artifact truth

Never infer that a source edit reached the preview from a successful build or rsync. Inspect the public HTML to identify the exact served hashed bundles, then inspect those public bundles for stable semantic markers and CSS rules.

For removed labels or copy:

- search all active locale namespaces and legacy page variants, not only the component currently believed to render;
- remove rejected prefixes everywhere they can surface (current/legacy components, every locale, and test fixtures), rather than only from the first matching translation key;
- verify the served JavaScript contains the replacement and does not contain the removed string;
- verify the public CSS contains the intended hierarchy rule;
- use a genuinely new asset hash or cache-busted URL when CDN caching may preserve an older bundle.

For hierarchy feedback, identify the exact visible text the user names before editing CSS. Pages often have an eyebrow/section label plus a separate H1; enlarging the H1 does not satisfy “make Platform overview bigger” when the user means the literal `Platform overview` label. Inspect the rendered DOM/component relationship, scope the rule to that exact label, and verify its public CSS selector and computed size. Do not report nearby-title changes as completion.

If the user says a change is not updated, trace source → build output → deployed directory → public HTML asset names → public bundle contents before making another speculative edit.

## Verification boundaries

Report these separately:

- service/runtime health;
- public API transport;
- authentication/session flow;
- required data loading;
- exact authenticated feature route and interaction;
- served visual/copy markers;
- production isolation.

HTTP 200 on the SPA, a rendered sign-in page, or a one-time API health check is not a functional preview.

### Completion language and review links

Use precise state labels:

- **Implemented:** code exists and local focused checks pass.
- **Publicly verified:** the exact public preview flow was exercised in a browser against the isolated API/database.
- **Deployed:** the approved change is integrated and verified on production.

For user-visible or transaction-flow fixes, do not stop at “implemented and pushed” when the user needs to evaluate behavior. Continue through publishing and public browser E2E verification, then include the exact public preview URL in the first completion-style response. If blocked, say “implemented, not yet publicly verified,” identify the missing gate, and do not call the work simply “fixed.” The user should not need to ask where the public link is.

When browser auth is seeded rather than entered through the form, inspect the application’s actual local-storage keys and stored user shape first. A valid API token under guessed key names can silently redirect to sign-in and produce a misleading feature failure. Prefer a real sign-in round trip; if seeding is necessary, verify `/auth/session` and the authenticated page request after seeding.

## Worktree-backed application instances

When a worktree is intended to be a separately running application rather than only a review build:

- Keep worktree creation defaults independent from runtime behavior. If worktrees are opt-in, live-app support must not silently enable them by default.
- A filesystem path is not an application URL. Define a durable process, unique loopback port, stable public route, health check, logs, restart behavior, and lifecycle state.
- Prefer stable path routing on an existing HTTPS host for MVP, e.g. `/worktrees/<stable-id>-<slug>/`, unless wildcard DNS/TLS is already available. Include the stable ID to prevent slug collisions.
- Require project-level launch configuration instead of guessing arbitrary repository commands: optional build argv, required start argv, health path, safe environment entries, and base-path support. Use structured argv, not shell strings, at the trust boundary.
- Model `not configured`, `stopped`, `starting`, `live`, `unhealthy`, and `failed` explicitly. Never report an unhealthy or merely running process as live.
- Use durable isolated services (normally templated systemd units), unique loopback ports, bounded logs, resource limits, and narrowly scoped privilege for service/web-server operations.
- Permit members to view status/open apps; restrict start/restart/stop/log mutations according to the host application's role policy.
- State the runner ceiling. One HTTP process per worktree is a valid MVP; Docker Compose/multi-service apps, root-only hosting, wildcard subdomains, and destructive cleanup are separate capabilities.
- Verify two instances concurrently and prove no port, route, process, asset, API, or mutable-data crossover. Also verify restart reconciliation, intentionally stopped state, and production isolation.

## Proposal correction pitfall

When a user corrects a preview proposal's default or lifecycle rule, update the canonical source and public review artifact everywhere: goal, architecture, task steps, API semantics, acceptance criteria, E2E, headings, badges, and open questions. Treat the correction as confirmed, preserve the implementation gate, and verify the public artifact contains the corrected phrase while the rejected assumption is absent; HTTP 200 alone is insufficient.

## Pitfalls

- Sharing a preview backed by a terminal/background process that exits with the agent session.
- Calling a preview functional after checking only its login page.
- Updating one i18n key while duplicate active keys retain rejected numbered labels such as section-spec prefixes.
- Reusing a cached hashed asset and assuming rsync invalidates CDN content.
- Reporting browser verification without exercising login and the exact data-backed route.
