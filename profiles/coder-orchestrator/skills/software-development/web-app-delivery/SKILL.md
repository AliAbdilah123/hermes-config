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

Always provide the real clickable URL; do not hand back placeholders like `<publicIP>`.

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

## Production Hardening Pass

When asked to refine an app until production-grade, include more than UI polish:
- Backend tests, JSON error envelopes, strict methods, request size limits, readiness endpoint, server timeouts, and security headers.
- Configurable env and no secrets in chat.
- SQLite outside the repo when deployed, WAL/busy timeout, and transactions for mutations.
- Frontend loading/error/empty states, disabled pending actions, focus/accessibility polish.
- Systemd service for backend and nginx-only public exposure.
- **Authentication/authorization for mutable public APIs.** For single-user/internal apps without full auth, add an `ADMIN_TOKEN` gate for POST/PUT/PATCH/DELETE while keeping safe GET endpoints public only if appropriate. The frontend should have a token entry UX and send the token only on mutating calls.
- **Clean release state.** Generated backend binaries, local SQLite DBs, and frontend dist output should not dirty git after deployment; ignore/remove them from tracking where appropriate.

References:
- `references/fullstack-app-production-hardening.md`
- `references/production-admin-token-and-systemd-cutover.md`

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
