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
5. Configure an explicit web-server route for both preview assets and preview API proxy; test configuration before reload.
6. Verify the public health endpoint, unauthenticated data endpoint, login/session round trip, authenticated workspace/data route, deep-link SPA fallback, and JS/CSS MIME types. Use a real preview-safe account or sign-up flow and cookie jar/browser session; a rendered login form is not authentication evidence.
7. Recheck service activity immediately before sending the URL. Recheck it after any gateway restart or long review delay. If the runtime was started through a chat-owned background process, replace it with the durable service before sharing—even if the process is currently healthy.
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

## Pitfalls

- Sharing a preview backed by a terminal/background process that exits with the agent session.
- Calling a preview functional after checking only its login page.
- Updating one i18n key while duplicate active keys retain rejected numbered labels such as section-spec prefixes.
- Reusing a cached hashed asset and assuming rsync invalidates CDN content.
- Reporting browser verification without exercising login and the exact data-backed route.
