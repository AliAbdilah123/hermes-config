---
name: web-app-delivery
description: "Use when building, scaffolding, deploying, exposing, smoke-testing, or debugging a web app on the default Hermes host stack. Covers React/TypeScript + Go + SQLite, nginx project paths, public URL delivery, service exposure failures, Tailscale/firewall/SELinux issues, and ARM64 headless browser visual verification."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [web, fullstack, react, typescript, go, sqlite, nginx, deployment, exposure, debugging, playwright]
    related_skills: [systematic-debugging, dogfood]
---

# Web App Delivery

## Overview

This is the umbrella workflow for delivering web applications on the Hermes Linux host: choose the default stack when unspecified, scaffold and build the project, run the backend under a stable process, expose the frontend/API through nginx, verify with real HTTP output and browser smoke checks, and debug exposure failures without guessing.

Use this as the class-level skill instead of separate one-session skills for “default stack”, “fullstack app”, “standard scaffold”, “release and expose”, “service unreachable”, or “ARM64 headless browser visual check” tasks.

## When to Use

Use this skill when the user asks to:
- Build a new web app and does not specify a stack.
- Scaffold a full-stack project with frontend, backend, and persistence.
- Make an app publicly reachable at `/projects/<projectName>/`.
- Produce a clickable public URL after deployment.
- Harden an existing app toward production quality.
- Refine an existing app that works but feels too corporate, dashboard-like, or data-first.
- Debug 404/502/timeouts involving nginx, backend ports, SELinux, firewall rules, Tailscale, loopback/localhost binding, or stale systemd/background processes.
- Run visual smoke tests with Playwright/Puppeteer/headless Chromium on ARM64 Linux.

Do not use it for non-web service operations unless the exposure/debugging pattern is directly relevant.

## Default Stack Contract

When the user does not specify a stack, use:
- **Frontend:** React + TypeScript via Vite, built to `frontend/dist`.
- **Backend:** Go HTTP server.
- **Database:** SQLite, usually `modernc.org/sqlite`.
- **API paths:** `/api/v1/*` locally, plus `/projects/<projectName>/api/v1/*` when exposed through nginx.
- **Public frontend:** `http://<actualPublicIP>/projects/<projectName>/`.

Stack lock rule: once the default stack is selected, do not silently replace React/TS, Go, or SQLite. Fix build/toolchain errors in place first. Ask before falling back to Python/FastAPI or plain HTML/JS.

## Design-System-First Product Builds

When the user supplies a design reference image or explicitly says to build the design system before the app, make that the first implementation milestone:
- Analyze the reference into tokens: colors, typography, spacing, radii, shadows, density, navigation, cards, tables, filters, charts, and interaction states.
- Implement reusable tokens/components before feature screens: app shell, cards/stat tiles, buttons, forms, badges/status pills, tables/lists, drawers/modals, score/progress visuals, and empty/loading/error states.
- Build product screens only from those components so the app feels coherent instead of a set of one-off pages.
- For SaaS/BI/dashboard products, seed realistic demo data and show complete flows even when external connectors/scanners are abstractions.
- Verify visual delivery with an actual served UI smoke check, not only a successful build.

Reference: `references/design-system-first-saas-bi-dashboard.md`.

### Visual Reference Fidelity Pass

If the user says the delivered app does not look like the supplied screenshot/reference, treat it as a fidelity bug, not as subjective polish:
- Reconstruct the visible screen to match the reference's component inventory and grid before changing colors at the margins.
- Make the reference-like state the first visible route for demo review; do not let a login screen or sparse empty state block visual comparison.
- Seed or hardcode realistic mock data for dashboards so KPI cards, opportunity rows, inboxes, summaries, progress/checklists, and CTA panels are populated.
- Rebuild, redeploy, then capture a real browser/headless screenshot of the served route and compare it to the source reference before reporting done.

Reference: `references/visual-reference-fidelity-dashboard.md`.

## Build and Scaffold Workflow

1. Create or use `~/projects/<projectName>` unless the user requested a different root.
2. Scaffold frontend with Vite React TypeScript and set `base: '/projects/<projectName>/'` in `vite.config.ts`.
3. Build frontend with `npm run build`; verify `dist/index.html` and `dist/assets/` exist.
4. Implement backend in Go with handlers registered before catch-all static serving.
5. Respect `PORT`, default to a free localhost port; bind final backend to localhost when nginx is the public entrypoint.
6. Build a persistent binary for final delivery and run via systemd or another supervised path. Use Hermes background processes only for temporary smoke testing. During systemd cutover, check for and stop any old manual/background process that still owns the target port before starting the service.
7. Verify backend directly before nginx: `curl -i http://127.0.0.1:<PORT>/api/v1/<endpoint>`.

See legacy/scenario references for concrete examples:
- `references/default-web-stack-legacy.md`
- `references/fullstack-app-legacy.md`
- `references/standard-stack-scaffold-legacy.md`
- `references/release-and-expose-web-app-legacy.md`

## Nginx Exposure Workflow

1. Inspect existing nginx includes and default server ownership before writing config. Do not assume `/etc/nginx/conf.d` or `/usr/share/nginx/html` is authoritative.
2. Prefer adding project-specific `location` blocks inside the existing port-80 default server rather than creating duplicate `server_name _` or duplicate `default_server` blocks.
3. Serve built static assets from a web-readable root such as `/var/www/html/projects/<projectName>/` or `/usr/share/nginx/html/projects/<projectName>/`.
4. Proxy project API paths to the backend:
   - `/projects/<projectName>/api/v1/` → `http://127.0.0.1:<PORT>/api/v1/`
   - Optionally retain `/api/v1/` compatibility only when it will not collide with another project.
5. Enable SELinux proxy support when needed: `sudo setsebool -P httpd_can_network_connect on`.
6. Run `sudo nginx -t` before reload.
7. Verify local nginx routes before declaring public success.

Template: `templates/release-and-expose-web-app-nginx-project-with-prds.conf`.

## Verification Order

Minimum real checks before reporting done:
1. Backend direct: `curl -i http://127.0.0.1:<PORT>/api/v1/<endpoint>`.
2. Nginx frontend: `curl -I http://127.0.0.1/projects/<projectName>/`.
3. Nginx project API: `curl -i http://127.0.0.1/projects/<projectName>/api/v1/<endpoint>`.
4. Browser/visual smoke check for user-facing UI when layout matters.
5. Public URL if network path allows. If same-host public-IP curl fails because of hairpin/NAT behavior but local nginx checks pass, report that caveat honestly.

When the built-in browser tool is slow or unavailable, a CLI headless Chromium screenshot is an acceptable visual smoke check if it produces a non-empty screenshot file and the rendered image is inspected. On Ubuntu snap Chromium, DBus/AppArmor warnings can appear while the screenshot still succeeds; verify the file exists and has bytes before treating it as failure.

Always provide the real clickable URL; do not hand back placeholders like `<publicIP>`.

## Mobile Responsive Layout Changes

When the request is specifically about mobile/small-screen behavior (hamburger menus, sidebars, topbars, dense dashboard cards, responsive rows):
- Preserve desktop behavior first; make the change breakpoint-scoped rather than rewriting the app shell.
- Prefer reusing the existing navigation content inside a drawer/overlay instead of maintaining a second duplicate nav tree.
- Add accessible controls: hamburger `aria-label`, `aria-expanded`, `aria-controls`; drawer/backdrop close affordances; Escape close where straightforward.
- Check `index.html` for a valid mobile viewport tag (`<meta name="viewport" content="width=device-width, initial-scale=1.0" />`). Missing viewport metadata makes mobile screenshots render a scaled desktop layout (often `innerWidth` around 980) even when CSS breakpoints look correct.
- After building, deploy the new `dist/` to the nginx-served path if the live URL is part of the deliverable, then verify `index.html` references the new hashed assets.
- Capture a real small-viewport screenshot (e.g. `390x844`) and confirm the persistent sidebar is gone and content stacks without horizontal squeezing.
- Verify mobile with DOM metrics, not only visual dimensions: `innerWidth`, `document.documentElement.scrollWidth`, and `horizontalOverflow = scrollWidth > innerWidth`. For a true 390px check, `innerWidth` and `scrollWidth` should both be about 390.
- If the target screen is behind auth, authenticate in the browser context with the real login API/session flow before capturing screenshots; do not accept a login-screen screenshot as proof that the dashboard is fixed.

References:
- `references/mobile-responsive-navigation-verification.md`
- `references/mobile-viewport-and-authenticated-visual-checks.md`

## Frontend Navigation/Auth Refinement Pass

When refining a deployed B2C/marketplace app's public homepage and header auth UX:
- Keep public discovery content visible before login: hero, public service cards, categories, and services-needed/posting categories.
- Put login/signup behind the nav entry point as a modal or dedicated page when the user asks for a cleaner header; avoid leaving demo-account selectors or auth forms floating/inline on the public landing.
- In authenticated headers, use an avatar/profile menu with accessible state (`aria-haspopup`, `aria-expanded`) and include user name/email, role badges, dashboard navigation, profile page navigation, and logout.
- Route dashboard to the best existing role-aware screen instead of creating a fake destination; implement a real profile page or visibly disable the item.
- Update tests to assert public content is visible logged out, demo login labels stay hidden until the modal opens, and avatar menu actions are visible after authenticated mock `/me`.
- Deploy and verify through nginx/public serving with DOM string checks plus a screenshot when the request is visual.

Reference: `references/frontend-nav-auth-refinement.md`.

## UX Humanization Pass

When the user says an app feels too corporate, dashboard-heavy, or data-first, treat it as an implementation request for a friendlier product surface — not just design advice. For member/community apps:
- Reframe the default/home screen around people, actions, and “what can I do now?” rather than metrics.
- Keep existing APIs, mutation handlers, auth/token behavior, and stack intact unless explicitly asked otherwise.
- Rename navigation and copy from admin terms (`Dashboard`, `Analytics`, `Audit`, `Command`) toward user terms (`Today`, `Circles`, `Events`, `My passes`, `Memberships`, `Safety log`) while leaving organizer/admin surfaces available but secondary.
- Add quick-action cards, upcoming event/session cards, feed/community pulse, wallet/status highlights, warm visual treatment, and mobile-first responsive cards.
- Build, deploy the updated dist, and smoke-test real served DOM for the new user-facing copy before reporting done.

Reference: `references/community-ux-humanization.md`.

## Consumer / Community UX Refinement Pass

When the user says an app feels too corporate, dashboard-like, or data-first, treat it as a product/UX-tone problem before treating it as a backend problem. Preserve the chosen stack and existing API behavior unless there is a clear data gap.

Use a people/action-first pass:
- Make the first screen answer: what can I do now, who can I connect with, and what is happening near me?
- Move analytics, audit logs, settings, and platform health behind secondary organizer/admin labels.
- Rename corporate sections into human terms where appropriate (Dashboard → Today, Programs → Circles, Sessions → Events, Analytics → Organizer view).
- Prefer warm hero copy, quick action cards, community feed/pulse, upcoming event cards, member wallet highlights, and human story cards over metric tiles and tables.
- Verify tone with a screenshot or DOM phrase smoke check, not only a successful build.

Reference: `references/consumer-community-ux-redesign.md`.

## External Worker / CRM Import MVPs

When extending an existing business/CRM app with CSV imports, template messaging, inboxes, or sidecar integrations such as Baileys/WhatsApp:
- Make import schemas backend-owned with a downloadable sample CSV endpoint.
- Model businesses and contacts separately with many-to-many associations when contacts can belong to multiple businesses.
- Support dotted template placeholders like `{{business.name}}` and render previews/sends through the same substitution logic.
- Treat external messaging workers as sidecars: keep the main API as source of truth, persist send attempts, and report honest `mock`/`queued`/`not_connected` states until the worker is configured and connected.
- For Baileys QR pairing, do not send only the raw QR payload to the frontend. Convert it in the worker to a browser-renderable PNG data URL, expose `qrAvailable` plus `qrDataUrl`/`qr`, proxy those fields through the authenticated app API, and make the UI poll while waiting to connect.
- Use nullable foreign keys for inbox/conversation rows that may not yet be tied to a business/contact; never write zero IDs into FK columns.
- Run sidecars under a supervised service for delivery; verify worker `/status`, backend-proxied status, frontend build, and deployed asset rather than stopping at code changes.

References:
- `references/business-crm-import-inbox-mvp-delivery.md`
- `references/business-crm-baileys-qr-display.md`

## Production Hardening Pass

When asked to refine an app until production-grade, include more than UI polish:
- Backend tests, JSON error envelopes, strict methods, request size limits, readiness endpoint, server timeouts, and security headers.
- Configurable env and no secrets in chat.
- SQLite outside the repo when deployed, WAL/busy timeout, and transactions for mutations.
- Frontend loading/error/empty states, disabled pending actions, focus/accessibility polish.
- Systemd service for backend and nginx-only public exposure.
- **Authentication/authorization for mutable public APIs.** For single-user/internal apps without full auth, add an `ADMIN_TOKEN` gate for POST/PUT/PATCH/DELETE while keeping safe GET endpoints public only if appropriate. The frontend should have a token entry UX and send the token only on mutating calls.
- **Proper app auth for multi-role products.** When a B2C app has customers/providers/admins, replace prototype identity shortcuts (`X-User-ID`, hardcoded demo identity, query-param user switching) with password-backed login, hashed passwords, opaque bearer sessions, `/me`, logout, and role-aware UI navigation. Route-level role checks are not enough: add object/participant authorization for direct-ID mutations (e.g. only a job customer can confirm/dispute/cancel/pay that job; only the assigned provider can start/submit proof). Verify with an unrelated-user direct-ID attack, not just hidden UI navigation. See `references/fullstack-app-authentication-hardening.md`.
- **Real pages, not empty navigation.** If the app has a sidebar/top nav, implement the pages users can reach (tables, detail flows, pipeline, generators, scripts, etc.) or visibly disable/grey out the nav item/button with `Soon`/`Segera Hadir`. Do not leave clickable placeholders, `href="#"` dead links, or buttons that imply unavailable functionality.
- **Visual-demo auth cleanup.** If a previous visual-reference pass temporarily bypassed auth to make screenshots easier, restore login/session/CSRF before calling the app production-grade.
- **Action-backed UI.** Primary actions on implemented pages must call real APIs and be verified. If an action is not backed by a real endpoint yet, disable it instead of showing a fake success.
- **Clean release state.** Generated backend binaries, local SQLite DBs, and frontend dist output should not dirty git after deployment; ignore/remove them from tracking where appropriate.

References:
- `references/fullstack-app-production-hardening.md`
- `references/production-admin-token-and-systemd-cutover.md`
- `references/production-grade-saas-mvp-pages-disabled-states.md`
- `references/siapjasa-xendit-mvp-delivery.md` — Xendit escrow mock, PRD provider correction, local Go toolchain pinning, and CLI Chromium visual smoke fallback from a marketplace MVP delivery.

## Exposure Debugging Playbook

When a service is “running” but unreachable, debug in layers:

1. **Listener:** `ss -tlnp | grep <PORT>` — determine whether it is `127.0.0.1`, `0.0.0.0`, Tailscale IP, or not listening.
2. **Process accept loop:** compare raw socket connect and `curl`; LISTEN with timeout can mean deadlocked accept/backlog, not firewall.
3. **Route/interface:** `ip route get <IP>` and compare loopback, host IP, and Tailscale IP.
4. **Firewall:** inspect iptables/nftables for interface-specific ACCEPT plus port-wide DROP. Local traffic may not enter via `tailscale0`.
5. **SELinux:** check nginx/httpd proxy denials and `httpd_can_network_connect`.
6. **Nginx upstream:** 502 usually means upstream stopped, wrong port, permission-denied env/executable, or route mismatch.
7. **Systemd:** read `journalctl -u <service> -n 80 --no-pager`; do not stop at `systemctl status`.

References:
- `references/service-exposure-debugging-legacy.md`
- `references/network-service-binding-legacy.md`
- `references/service-exposure-debugging-iptables-tailscale-port-block.md`
- `references/network-service-binding-iptables-port-names-pitfall.md`
- `references/network-service-binding-service-exposure-checklist.md`

## ARM64 Headless Browser / Visual Smoke Checks

On ARM64 Linux, browser automation failures are often host/browser mismatch rather than app bugs.

Decision tree:
1. If Docker is available, prefer `mcr.microsoft.com/playwright:<version>-noble`/`jammy` for a known-good browser environment.
2. If running host-local, use Playwright Chromium rather than Google Chrome ARM64 flows.
3. Do not run `playwright install-deps` on RHEL/Oracle hosts where it will attempt Debian/apt commands.
4. Map missing libraries to host packages (`dnf install gtk3 atk at-spi2-core cups-libs libxkbcommon alsa-lib mesa-libgbm libXcomposite libXdamage libXfixes libXrandr libdrm`).
5. Verify a minimal browser launch before using it as the app smoke test.

References:
- `references/browser-arm64-headless-legacy.md`
- `references/browser-arm64-headless-session-2026-05-31-arm64-headless.md`

## Common Pitfalls

- Missing Vite `base` makes built assets request `/assets/...` instead of `/projects/<project>/assets/...`.
- Duplicate port-80 default server blocks can make `nginx -t` pass while the intended route is ignored.
- Nginx `alias` and `root` behave differently; path doubling causes confusing 404s.
- Home-directory static serving often fails under SELinux; copy built assets to a real web root.
- Root `/api/v1/` aliases can collide across projects; prefer project-prefixed API paths for deployed apps.
- Do not leave final delivery dependent on an agent-owned background process.
- Public-IP curl from the same instance may fail due to hairpin routing; verify localhost nginx and ask user to check externally if needed.
- Port names in iptables output may resolve numerically (`9119` → `mxit`); use numeric listing and exact rule specs.

## Verification Checklist

- [ ] Stack matches user request or default contract.
- [ ] Frontend build completed and assets are readable by nginx.
- [ ] Backend was built and started under a stable runtime.
- [ ] Direct backend API returns expected status/body.
- [ ] Nginx config is included, tested, and reloaded.
- [ ] Project frontend and project-prefixed API work through localhost nginx.
- [ ] Browser/visual smoke check completed when UI is part of deliverable.
- [ ] Final answer includes a real URL and real verification output/caveats.
