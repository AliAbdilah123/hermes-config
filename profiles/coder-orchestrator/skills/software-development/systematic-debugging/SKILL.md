---
name: systematic-debugging
description: "4-phase root cause debugging: understand bugs before fixing."
version: 1.1.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, troubleshooting, problem-solving, root-cause, investigation]
    related_skills: [test-driven-development, plan, subagent-driven-development]
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Someone wants it fixed NOW (systematic is faster than thrashing)

## The Four Phases

You MUST complete each phase before proceeding to the next.

---

## Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

### 1. Read Error Messages Carefully

- Don't skip past errors or warnings
- They often contain the exact solution
- Read stack traces completely
- Note line numbers, file paths, error codes

**Action:** Use `read_file` on the relevant source files. Use `search_files` to find the error string in the codebase.

### 2. Reproduce Consistently

- Can you trigger it reliably?
- What are the exact steps?
- Does it happen every time?
- If not reproducible → gather more data, don't guess

**Action:** Use the `terminal` tool to run the failing test or trigger the bug:

```bash
# Run specific failing test
pytest tests/test_module.py::test_name -v

# Run with verbose output
pytest tests/test_module.py -v --tb=long
```

### 3. Check Recent Changes

- What changed that could cause this?
- Git diff, recent commits
- New dependencies, config changes

**Action:**

```bash
# Recent commits
git log --oneline -10

# Uncommitted changes
git diff

# Changes in specific file
git log -p --follow src/problematic_file.py | head -100
```

### 4. Gather Evidence in Multi-Component Systems

**WHEN system has multiple components (API → service → database, CI → build → deploy):**

**BEFORE proposing fixes, add diagnostic instrumentation:**

For EACH component boundary:
- Log what data enters the component
- Log what data exits the component
- Verify environment/config propagation
- Check state at each layer

Run once to gather evidence showing WHERE it breaks.
THEN analyze evidence to identify the failing component.
THEN investigate that specific component.

### 4a. SPA Auth UI / Build-Time Env Triage

When a deployed Vite/React auth route shows the wrong login experience (fallback/basic form instead of provider UI) or a partial provider UI (for example only a card separator/strip line):
- Inspect **build-time frontend env at the app build root**, not just the repository root env. Vite only exposes `VITE_*` vars at build time and auto-loads env files relative to the directory running `vite build`.
- Verify the **served bundle** contains the expected provider URL/config and not an `undefined`/fallback expression. Source files and `.env` are not enough evidence.
- Check provider UI prerequisites: required CSS import and context/provider wrapper. For Neon Auth UI, `<AuthView />` needs `@neondatabase/auth-ui/css` (or Tailwind variant) and `NeonAuthUIProvider` with the Neon auth client; otherwise it may render only a skeleton/separator.
- Verify with rendered DOM markers for real fields/buttons (`Sign In`, `Email`, `Password`) after deploy, not just HTTP 200 or asset presence.

See `references/vite-spa-auth-ui-triage.md` for the detailed checklist and verification recipe.

### 4a.1 SPA Session Cache Staleness After Auth

When sign-in succeeds (API returns 200 with user data) but the page immediately shows "session
not established" or redirects back to login: suspect a module-level session cache that still
holds `{ data: null }` from the pre-auth page load. After sign-in, `getSession()` returns the
stale cache instead of making a real request. Fix: use a force-refresh variant
(`refreshSession()`) or clear the cache before calling `getSession()`.

See `references/spa-session-cache-staleness-after-auth.md` for the pattern, detection, and fix.

### 4b. OAuth/App-ID Error Triage

When a user reports a social login/OAuth "Invalid App ID" or "app id error" after updating env:
- Inspect the **running service environment**, not just repository env files. For systemd, find `EnvironmentFile=` and compare it to `/proc/<pid>/environ` with values masked.
- Generate the deployed OAuth start URL and parse provider URL parameters safely: app/client id length and last 4 chars, redirect URI, scopes, provider host/path.
- Check for stale project paths in `redirect_uri`, frontend base URL, and provider cancel URLs.
- If multiple env aliases exist for the same app id, prefer canonical provider ids (e.g. `META_APP_ID`/`FACEBOOK_APP_ID`) over legacy product-specific aliases that may contain stale or secret-shaped values.
- Verify by fetching the provider dialog with redirects enabled and confirming it no longer contains the invalid-app-id page and reaches login/oauth flow.

See `references/oauth-provider-env-precedence.md` for the detailed recipe and fix pattern.

### 4b. Vite Frontend Env Missing After Deploy

When a Vite/React production page renders a fallback UI instead of a provider integration (auth widget, analytics, payment, etc.) even though the repo has the right env values:
- Inspect the **compiled deployed JS bundle**, not just source files or root `.env`. Search for the expected provider URL/domain and for inlined-undefined patterns like `(void 0)?.trim`.
- In monorepos, confirm where the build runs. Vite auto-loads env files from the Vite app root (`envDir`, default current app root), so a repo-root `.env` may be ignored by `apps/web` builds.
- Put `VITE_*` values in the app root env file, export them during the build, or configure `envDir` intentionally.
- Rebuild and publish the new hashed `dist/` asset, then fetch the public HTML/JS to verify the provider literal is present and the old undefined expression is gone.

See `references/vite-deployed-env-triage.md` for a compact reproduction/fix recipe.

### 4b. SPA Subpath API and Asset Routing

When a deployed SPA lives under a subpath (for example `/projects/<app>/`) and login or API actions show generic `request_failed` while the backend is healthy:
- Compare the root-relative API URL (`/api/v1/...`) against the mounted proxy URL (`/projects/<app>/api/v1/...`). A root-relative request can bypass the app's Nginx location and return 404 or hit the wrong service.
- Inspect the **served production JS bundle** for API URL construction. A source helper may use `import.meta.env.BASE_URL`, but code like `path.startsWith('/api/') ? path : apiPath(path)` silently skips the base path for the exact API routes that need it.
- Fix at the API-path helper so all API calls normalize through the base-aware route builder; do not patch individual login calls only.
- Verify with browser/network evidence that login, `/me`, and post-login workspace/data requests all target `/projects/<app>/api/...` and return 200.

When the page itself is blank but HTML returns `200`:
- Inspect the served HTML for root asset URLs (`/assets/index-*.js`, `/assets/index-*.css`) vs the mounted subpath (`/projects/<app>/assets/...`).
- Check the domain-specific Nginx server block as well as the default/IP block; they may have different `sub_filter` or `alias` behavior.
- Prefer rebuilding Vite with the correct `base` (`/projects/<app>/`) over relying on Nginx HTML rewriting.
- Verify with cache-busted public HTML and direct JS/CSS `HEAD` probes for `200` and correct content types. If mobile browsers still show blank, tell the user to force-refresh/clear site cache.

See `references/spa-subpath-api-routing.md` for the API checklist and `references/spa-subpath-asset-base-domain-routing.md` for the blank-page asset-base recipe.

### 4c. Browser FFmpeg / Video Export Performance Triage

When a browser video editor/export flow feels slow:
- Inspect the **actual generated FFmpeg arguments** before proposing platform rewrites. Full re-encode flags (`-c:v libx264`, `-c:a aac`, CRF/preset) are usually the bottleneck; `-c copy` is a fundamentally different fast path.
- Check seek placement. `-i input -ss START` favors accurate output but can decode extra frames; `-ss START -i input` is much faster and often sufficient for fast/keyframe-near cuts.
- Check whether each slice is exported as a separate sequential job and whether the whole source file is copied into a browser/WASM virtual filesystem.
- Benchmark fast-copy, exact re-encode, and fast-seek re-encode variants with a representative source before recommending native mobile or server architecture.
- Prefer a product fix that exposes modes: **Fast Export** (input seek + stream copy) by default, **Exact Export** (frame-accurate re-encode) as the slower option, and server-side/native FFmpeg for long videos or batch reliability. Native Android can help, but it is not the root fix if the algorithm still re-encodes every clip sequentially.

See `references/browser-ffmpeg-export-performance.md` for command patterns, benchmark setup, and a fix decision tree.

### 5. Trace Data Flow

**WHEN error is deep in the call stack:**

- Where does the bad value originate?
- What called this function with the bad value?
- Keep tracing upstream until you find the source
- Fix at the source, not at the symptom

**Action:** Use `search_files` to trace references:

```python
# Find where the function is called
search_files("function_name(", path="src/", file_glob="*.py")

# Find where the variable is set
search_files("variable_name\\s*=", path="src/", file_glob="*.py")
```

### 4d. SQLite Runtime DB Deleted / Misleading Auth Errors

When a deployed SQLite-backed app suddenly reports duplicate-user errors for brand-new signup attempts, or login succeeds but the next session check is `null`:
- Inspect the running service's configured DB path and the process file descriptors before restarting. If the DB was deleted while open, `/proc/<pid>/fd` may show `app.db (deleted)`.
- Recover the live DB from the open file descriptor before restart, then restore the configured runtime DB path with correct ownership.
- Treat this as two bugs: runtime data-path loss plus auth error masking. Fix auth handlers so only unique constraint failures return `USER_ALREADY_EXISTS`; generic DB/session failures should return explicit 500 errors and must not be ignored.
- Verify with direct public-route signup, session, signout, login, and session checks using a cookie jar.

See `references/sqlite-runtime-db-recovery-and-auth-errors.md` for commands and the full recovery/fix recipe.

### 4d.1 SQLite WAL Corruption After Live-DB Copy or Crash

When a copied or restarted SQLite database causes the Go API to crash-loop with `database disk image is malformed (11)`:
- Remove the destination `-wal` and `-shm` files, then verify `PRAGMA integrity_check` on the main DB before restarting the service.
- The WAL belongs to the original process; copying it to a new process is unsafe unless the original process was stopped cleanly.
- For safe offline copies: use `sqlite3 .backup` or `VACUUM INTO` instead of raw `cp` of all three files.
- Verify the service starts and `/health` returns 200.

See `references/sqlite-wal-recovery-after-copy.md` for the full recovery recipe.

### 4d.2 Go Binary Stale Build / Source Changes Not Reflected

When you modify Go source, `go build` succeeds, deploy, but the running service does NOT reflect your changes — the binary was compiled from cached `.a` files predating the edits:
- Verify with `strings /path/to/binary | grep "unique_literal_from_your_change"`. No match → stale binary.
- Clean the cache and rebuild: `go clean -cache && CGO_ENABLED=1 go build -o /path/to/binary .`
- Also confirm the binary deploys to the path expected by systemd: `systemctl cat <service> | grep ExecStart`.
- A stale-binary symptom can actually be a wrong-deployment-path symptom. Check both.

See `references/go-build-cache-stale-binary.md` for the full diagnostic and prevention pattern.

### 4e. Systemd Restart After `.env` Changes

When the user updates `.env` and asks to restart a deployed Linux service:
- Inspect the unit (`systemctl cat`) to confirm the actual `EnvironmentFile=` and `WorkingDirectory=`. Do not assume the edited `.env` is the one the service reads.
- After `systemctl restart`, verify the service after a short delay; it may enter an auto-restart loop even though the restart command returned successfully.
- If logs show `bind: address already in use`, identify the listener with `ss -ltnp` and compare the app's actual env variable names (`ADDR` vs `PORT`, etc.) before changing ports or killing processes.
- Fix the persistent env file read by systemd, restart, then verify both unit state and the expected listening socket.

See `references/systemd-service-restart-env-port-triage.md` for commands and pitfalls.

### 4f. Deployed SPA API 502 / Stopped Upstream Service

When a deployed SPA shows an API-load error and the public subpath API returns Nginx `502 Bad Gateway`:
- Confirm whether the expected upstream service is inactive or the upstream port is unbound before touching application code.
- Probe both the local upstream route and the public proxied route; a stopped API usually yields local connection failure plus public `502`.
- Check `systemctl status` and recent `journalctl` logs for the app API service. If it is simply `inactive (dead)`, restart it and verify it stays `active` after a short delay.
- Verify the exact deployed API prefix after recovery (`/projects/<app>/api/v1/...` vs `/api/...`), because a wrong prefix can still return `404` even when the API is healthy.

See `references/deployed-api-stopped-nginx-502.md` for a compact command recipe.

### 4h. Cloudflare CDN Stale Cache (Images Served as HTML / Wrong Content-Type)

When a deployed SPA has broken image previews (showing broken/blank thumbnails) even though the origin serves the correct image:

- Check **origin directly** (curl 127.0.0.1) vs **public CDN-proxied URL**. If origin returns `Content-Type: image/jpeg` and the public URL returns `content-type: text/html` with `cf-cache-status: HIT`, Cloudflare has cached an HTML fallback page (SPA index or nginx error page) as the image.
- Root cause: the nginx config was missing the proxy location for the image path when the URL was first requested. The SPA fallback HTML got cached with the image URL and a high `max-age` (typically 14400s / 4 hours).
- **Two-pronged fix:**
  1. Add proper `Cache-Control: public, max-age=31536000, immutable` at the origin handler so future CDN entries are correct image types with long-lived cache.
  2. Append a cache-buster query parameter (`?v=<updatedAt or mtime>`) to image URLs in API responses so the frontend requests bypass stale CDN entries immediately.
- Verify with: `curl -sI '<public-url>' | grep -E 'content-type|cf-cache-status'` — MISS or EXPIRED for the cache-busted URL, HIT with `text/html` for the stale URL.
- For new uploads, unique filenames avoid the problem. The cache-buster is only needed for recently-cached stale entries.

See `references/cloudflare-cdn-stale-image-cache.md` for the command recipe and nginx/origin header patterns.

### 4g. SQLite-Backed Go API Hangs While Health Is OK

When a Go API using SQLite shows client-side `Request timed out` on login/signup or slow dashboard rendering, but `/health` and `systemctl status` look healthy:
- Reproduce locally against `127.0.0.1:<port>` before assuming browser, DNS, Cloudflare, or nginx issues.
- Compare endpoints: `/health` (no DB), a DB GET (`get-session`/dashboard), a POST without DB/body, then auth POST with JSON. If health works and auth POST hangs, suspect a blocked DB connection or request goroutine.
- For SQLite with `db.SetMaxOpenConns(1)`, inspect background goroutines (publishers/schedulers/sync jobs). A goroutine that holds the only DB connection while doing external HTTP calls can starve login and dashboard requests.
- A service restart is a valid immediate mitigation, but the permanent fix is to release DB rows before network calls, use a separate publisher DB handle, raise connection capacity carefully, and set strict publisher HTTP timeouts.
- Verify by making auth POST return quickly with either `401` for bad credentials or `200` for valid credentials.

See `references/go-sqlite-backend-hang-timeout.md` for the detailed triage and fix recipe.

### 4h. Go SQL Query Construction / Dynamic WHERE Bugs

When a SQL query works in `sqlite3` CLI but fails via the Go API with `"SQL logic error: near '<token>': syntax error"`:
- The query string is likely constructed with string concatenation in Go, not sent as a static template.
- Trace every branch in the WHERE clause builder; count opening vs closing parentheses per conditional path.
- When testing HTTP API endpoints with auth tokens, prefer Python (+ `urllib`) over `curl` — shell escaping can silently corrupt long tokens (UUID concatenations).

See `references/go-sql-query-construction-debugging.md` for a compact diagnosis recipe.

### 5a. Frontend/API Shape Drift (`.filter` / `.map` is not a function`)

When a React/Vite page shows a runtime collection error such as `t.filter is not a function`:
- Trace the value back to the `apiClient.get<T>()` boundary; the generic type may not match runtime JSON.
- Probe the real deployed/local endpoint and inspect the top-level JSON shape. A common mismatch is frontend expecting `Item[]` while the API returns `{ data: Item[] }` or a paginated envelope.
- Fix with a small typed response normalizer/unwrap helper at the API consumption boundary, not by hiding the symptom with optional chaining around array methods.
- Add a regression test whose mock uses the real API envelope shape that previously failed.
- Verify the targeted test, build/typecheck, and if deployed, fetch the served bundle/API to confirm the deployed artifact includes the normalizer and the endpoint shape is understood.

**Variant: Zod validator field mismatch → silent button failure.** When CRUD toggle buttons appear to work (optimistic UI updates) but the backend never receives the change, with no console or network errors: compare the frontend payload field names against the backend Zod schema. Zod silently strips unknown fields by default. Match field names or switch to the correct endpoint. See `references/zod-validator-field-mismatch.md` for detection and fix patterns.

See `references/frontend-api-shape-drift.md` for a compact recipe and minimal TypeScript pattern.

### 5a.1 Frontend/API Unknown Enum Runtime Crash

When a deployed React/Vite page is blank even though HTML/assets return 200, and the browser console shows a render-time lookup error like `Cannot read properties of undefined (reading 'bg')`:
- Treat frontend DTO unions as hypotheses, not proof. Probe the real deployed API payload for enum-ish fields used as lookup keys (`imageTone`, status, variant, theme, etc.).
- Compare runtime values against object-map keys. New backend values such as `green`/`blue` can crash code that assumes only `warm`/`cool`/`ink`/`accent`.
- Fix at the lookup boundary with a safe fallback (`MAP[value] ?? MAP.default`) and, if values are legitimate, add/normalize supported styles/types deliberately.
- Apply the pattern across similar lookup tables and verify with a real browser/CDP runtime exception check plus a public cache-busted URL.

See `references/frontend-unknown-enum-runtime-crash.md` for the reproduction/fix recipe.

### 5b. UI Metric vs. Global Data Count Questions

When a user asks whether a displayed count (for example `18/18 TAKEN`, badge counts, usage counters, quota indicators) implies a global entity count:
- Treat the screenshot as a symptom label, not proof of the underlying data model. Identify the UI field's source before answering.
- Distinguish **scoped operational metrics** (session seats taken, pending approvals for one program, per-product capacity) from **global records** (registered users, program members, claims/bookings across the site).
- Inspect the runtime state or API response that feeds the screen and separately count the relevant global table/list. If the app uses a mock/blob state store, parse the blob and report both the stored display metric and the actual backing records visible in that store.
- If a displayed count is seeded/demo aggregate data rather than derived from individual records, say so explicitly; do not imply that each unit has a visible row unless verified.
- Final answer should be concise: “X means scoped metric A, not global count B; verified global count is N; caveat if demo/seeded aggregate.”

### 5b.1 Multi-Timezone UI Display vs Logic Drift

When a user reports that event/session times are wrong, or a session shown as already over is not moved into past/completed sections:
- Trace both layers separately: the **display formatter** (`toLocaleTimeString`, `timeZone`) and the **categorization logic** (`isPast`, `getDayGroup`, filters). They may use different timezone sources.
- Search for hardcoded timezone literals in React/Vite display components (`timeZone: 'America/New_York'`) while parent pages/API data use program/tenant timezone.
- Pass the tenant/program timezone through props and use it consistently for date pills, clock labels, and day grouping.
- Watch for date-only grouping: `date(start) === today` does not mean the session is still active if `endTime < now`.
- Watch for `return 'past'` fallthrough in grouping helpers; future sessions beyond tomorrow can be mislabeled as past.

See `references/decoupled-timezone-sources.md` for detection commands and the Komuna example.

### 5b.2 Frontend Filter / API Query Triage

When UI filter pills/tabs visually switch but the results stay on the default set (for example session filters where Ongoing/Past still show Upcoming):
- First verify the frontend actually sends the selected filter value in the API params; add an interaction test that clicks the filter and asserts the request shape.
- Probe the active API endpoint directly for each query value and inspect distinct returned item statuses, not just HTTP 200.
- Check the backend list handler for ignored query params, especially branches that return all rows when pagination params are present.
- For time-range status, compute with both start and end (`now < start` upcoming, `start <= now < end` ongoing, `now >= end` past); start-only logic can never produce ongoing.
- If routes use slugs, resolve slug to canonical ID before comparing foreign keys in subresource handlers.
- Preserve already-correct layouts unless the user explicitly asks for visual changes; fix data/status and dynamic headings only.

See `references/frontend-filter-api-query-triage.md` for a compact reproduction/fix checklist.

### 5b.2 Client-Side Filter Hardcoded Stubs

When a location/permission-based UI filter shows "no results found" even after the user grants the permission (geolocation, camera, etc.), or when a filter with multiple options always produces the same fixed subset — suspect a hardcoded stub left in production:

- Trace the permission callback: does it capture the actual data (coordinates) or just flip UI state?
- Inspect the filter function body for hardcoded literal comparisons (`p.location === 'Brooklyn, NY'`, `return false`) in switch/case or if/else branches.
- If the backend stores location as text only, you may need a static city→[lat,lng] map + Haversine formula for client-side distance calculation.
- Clarify with the user whether they want filtering (exclude far items) or sorting (show all, nearest first) — the implementation strategy differs.
- **After code fix, verify i18n/locale files are clean.** Hardcoded display text (e.g. "Brooklyn, NY") often survives in `i18n/en.json` rendered via `t('key.path')` and won't show up in component code searches. See references/client-side-filter-hardcoded-stubs.md § i18n/locale.

See `references/client-side-filter-hardcoded-stubs.md` for the full triage checklist, fix pattern, and Haversine reference.

### 5c. SQLite JSON-State Role Seeding / Demo Admin Access

When a SQLite-backed app stores auth records in normal tables but product/domain state in a JSON blob (for example `app_state.payload`) and users appear to gain admin/manager dashboards unexpectedly:
- Inspect auth tables and JSON blob state separately. `auth_users`/sessions answer who can log in; JSON `Members`/`Roles` often answers what dashboards they see.
- Preserve existing auth identities while seeding: upsert by email/id, then assign them into programs in the blob. Do not overwrite existing users with fixture-only accounts unless requested.
- Search for fallback workspace/access code that grants default admin/superadmin roles when unauthenticated, no membership exists, or a dev user is active. If present, remove/fix the fallback; changing roles in seed data will not solve automatic admin access.
- Back up the DB before rewriting the JSON blob, then verify role aggregates and real signed-in `/me/workspace` responses for the intended manager, ordinary user, and superadmin.
- See `references/sqlite-json-state-role-seeding.md` for the compact recipe and verification checklist.

### 5d. Payment Provider Active-vs-Stub Triage

When the user asks whether a deployed payment integration is active (Xendit, Stripe, Midtrans, etc.):
- Do not stop at source-code presence or env-file values. Inspect the **running service environment** and the **actual deployed checkout response**.
- Separate three states explicitly: provider credentials valid, provider mode (`test`/`live`), and application flow active. A valid provider key can coexist with a stub checkout path.
- Probe the provider with a safe read-only endpoint when credentials are available (for Xendit, a basic-auth `GET /v2/invoices?limit=1` is enough to validate the key without creating a payment).
- Trigger the local/public checkout endpoint with a harmless/demo package if available and inspect whether it returns a real provider invoice/hosted-checkout URL or a stub/local URL such as `checkout-stub.local`.
- Check the running implementation, not only the newer/reference implementation in the repo; deployed services may use a fallback Go/SQLite or mock API while TypeScript provider code exists elsewhere.
- Final answer should distinguish: “credentials are valid/test/live” from “website checkout uses real provider” and include the public URL plus concise root cause if inactive.

### 5e. Hermes Kanban Blocked Task Triage

When the user asks why tasks are blocked in a Hermes kanban board:
- Inspect the board's SQLite state and logs, not just the visible status label. Board data commonly lives under `~/.hermes/kanban/boards/<board>/` with `kanban.db`, `board.json`, and per-task logs.
- Query `tasks`, `task_events`, `task_runs`, `task_comments`, and `task_links` to distinguish actual failure from review handoff, manual reclaim, dependency blocking, or stale auto-claim cleanup.
- Treat `blocked` with a run summary like `review-required: ...` as an intentional human-review gate, not a task failure.
- If events show `claimed/spawned` followed by `reclaimed` with a reason such as “auto-claimed before dependencies complete,” report that the task was stopped because its parents were incomplete, then identify the dependency chain from `task_links`.
- Read the specific task log only after event/run metadata identifies which task needs explanation; logs may be empty if the task was reclaimed immediately.
- Final answer should list the blocked tasks by ID/title and state the root cause category for each: review-required, dependency chain, failed run, or stale/manual reclaim.

### 6. External OAuth Provider Errors

**WHEN a social login/connect flow fails with provider errors (Meta/Facebook/Instagram, Google, etc.):**

- Separate app-generated URL bugs from provider-dashboard configuration issues.
- Parse the generated OAuth URL and verify `client_id`, `redirect_uri`, scopes, and provider version/path.
- Compare environment aliases and precedence; stale legacy env names can silently override the intended app id.
- Probe the provider authorization URL directly with `curl -L -A 'Mozilla/5.0'` and inspect effective URL/body for provider-specific errors.
- If app id is accepted but provider says the app is inactive/not available, stop code changes and check provider dashboard mode, roles/testers, products, and permission approval.

For Meta/Facebook-specific diagnostics, see `references/meta-oauth-app-id-active-status.md`.

### 6a. Social Scheduler False-Published / Cross-Provider Account Bugs

When a social scheduler says a post is published but it does not appear on Facebook/Instagram, or connecting Facebook makes Instagram look connected:
- Trace status transitions first; remove any read-handler/scheduler stub that marks posts `PUBLISHED` without provider API calls.
- Verify per-platform target rows, not just parent post status. Billing/quota should count only provider-confirmed target success.
- Check account tables store the credentials required for the publish API. Instagram image publishing needs an IG user id and access token; if only id/username/expiry are persisted, real publishing is impossible until reconnect after adding token storage.
- Keep provider account models separate unless the product explicitly wants cross-provider linking. Facebook Pages exposing `instagram_business_account` should not automatically create direct Instagram accounts if the UI treats direct IG connect separately.
- Filter reconnect/expiry banners by the real provider; stale cross-provider rows can keep warning users after a successful direct reconnect.
- Do not replace **Disconnect** with **Reconnect** for expired accounts when the user asks for disconnect; always let users disconnect stale/broken social accounts.
- Use real provider success signals: Instagram media container + `media_publish` media id, Facebook external `page_id` publish id.
- For Meta Business Login, support a dashboard-provided `config_id`; forcing `auth_type=rerequest`/profile selector helps but does not guarantee the Business onboarding screen without the config id.

See `references/social-publishing-oauth-triage.md` for the compact checklist and provider-specific pitfalls.

### 6a.1 Social Comment Sync / Moderation Bugs

When a social comment-management UI shows stale Instagram comments, local replies do not appear on Instagram, comment likes do not increase on Instagram, or delete/moderation actions are missing:
- Separate local UI state from provider-visible state. Rows in `instagram_comments`/`comment_likes` only prove the app changed locally; Instagram-visible actions require provider comment IDs and valid manage-comments scopes.
- Persist the Instagram comment/reply ID returned by Graph API for top-level comments and replies. Without that mapping, later reply/like/unlike/delete can only be local.
- Sync before listing: fetch provider comments plus nested replies and `like_count`, upsert them locally, then return local rows so latest Instagram data and just-created local rows are both visible.
- Likes and moderation should call provider endpoints when a provider comment ID is known: `POST /{comment-id}/likes`, `DELETE /{comment-id}/likes`, and `DELETE /{comment-id}`.
- In post detail UIs, keep performance metrics in a stable side panel next to media on desktop; open comments as a right-side drawer/dialog so it does not cover performance.
- See `references/social-comments-sync-and-moderation.md` for endpoint patterns, verification, and deployment checks.

### Phase 1 Completion Checklist

- [ ] Error messages fully read and understood
- [ ] Issue reproduced consistently
- [ ] Recent changes identified and reviewed
- [ ] Evidence gathered (logs, state, data flow)
- [ ] Problem isolated to specific component/code
- [ ] Root cause hypothesis formed

**STOP:** Do not proceed to Phase 2 until you understand WHY it's happening.

### Hardcoded Mock Values Left in Production Handlers

When a user reports that a metric or quota is wrong (e.g. "Avg Engagement Rate is 4.7% with 0 posts", "post quota didn't increase after payment"), before assuming a data-flow or DB issue, **grep the API handler for hardcoded literal values**:

- Dashboard handlers that return `tier: "FREE"` or `publishedLimit: 10` regardless of the actual subscription row.
- Analytics handlers that return fixed `avgEngagementRate: 4.7, totalReach: 4200` regardless of post count.
- Any handler that constructs a response map with literal numbers/strings instead of querying or computing from real data.

This is common in migrated/parity apps where placeholder values were left during initial stubbing and never replaced with real queries. The fix is to call the real data function (e.g. `models.SubscriptionData(db, userID)` or a computed summary) and use its output in the response map. Add a unit test that verifies zero/empty input produces zero output.

### Frontend Theme / Mobile Dark-Mode Notes

When a mobile browser appears dark while the app state says light, or toggling dark mode makes text/logo contrast worse:
- Inspect theme state (`localStorage`, root `.dark` class) separately from browser color-scheme behavior.
- Check the actual CSS variables used by components, not only framework tokens. If components use `var(--ink)`, `.dark` must make `--ink` a light/readable color.
- Add `color-scheme` hints (`:root`, `.dark`, and the HTML meta tag) to prevent mobile browser auto-darkening/form-control mismatch.
- Keep logo/brand colors on stable brand tokens instead of text tokens so the logo is not inverted or washed out by theme changes.
- Avoid active states like `bg-[var(--ink)] text-white` if `--ink` changes across themes; use primary/dedicated semantic tokens.
- For depth/shadow effects, do not reuse light-mode text tokens as shadow colors. In dark mode `--ink-*` is often light, so `box-shadow: ... var(--ink-1)` creates pale mist/glow instead of realistic depth. Add `.dark` overrides that use real black/transparent black shadows and reduce accent/noise opacity.
- See `references/frontend-theme-color-scheme-and-dark-mode.md` for a compact recipe and regression-test pattern.

### Responsive UI Regression Notes

When the issue is a responsive layout regression, especially one described as "not responsive like the original":
- First identify shared layout components used by all affected routes; fix the shared component before duplicating route-level tweaks.
- Compare against the original/reference implementation, but convert fixed inline dimensions/positions into breakpoint-aware classes rather than restoring rigid values.
- Verify both the component and its parent wrapper; a responsive child can still fail if the parent is hidden at the wrong breakpoint or uses height classes without a concrete containing height.
- For data-heavy tables that overlap or clip on phones, inspect fixed table widths, long unwrapped cell contents, and horizontal-scroll state. Prefer a mobile card presentation below phone breakpoints while preserving desktop tables. See `references/responsive-data-table-mobile-cards.md`.
- When overriding shadcn/ui `DialogContent` (or any component with breakpoint-prefixed defaults), match the same breakpoint prefix. `max-w-4xl` is silently ignored because `sm:max-w-sm` uses a different prefix; use `sm:max-w-4xl`. See `references/shadcn-ui-dialog-width-override.md`.
- Use screenshot-based viewport checks after implementation. See `references/responsive-ui-regression-qa.md` for a compact recipe, including Vite base-path and Chromium `--virtual-time-budget` tips.

### SPA Auth Provider / Login UI Notes

When a deployed SPA shows the wrong login UI (hosted provider UI, basic fallback, missing OAuth button, or a skeleton/strip instead of a form):
- Confirm the intended auth mode before fixing. Do not assume OAuth/hosted auth is desired just because provider env vars exist; the correct product requirement may be first-party/local login.
- Check build-time frontend env scope, not just root env files. Vite only inlines `VITE_*` variables visible to the frontend build process; nested apps may not load a repository-root `.env`.
- If enabling a third-party auth UI, verify the required provider/context wrapper and CSS import, not only the page component.
- If reverting to local/basic auth, remove temporary frontend env files such as `apps/web/.env.local` before rebuilding so the deployed bundle does not keep selecting the hosted provider path.
- Verify the public deployed artifact with a cache-busted URL and DOM/text markers for both intended labels present and unintended provider labels absent.
- See `references/spa-auth-provider-env-and-fallbacks.md` for a compact checklist.

---

## Phase 2: Pattern Analysis

**Find the pattern before fixing:**

### 1. Find Working Examples

- Locate similar working code in the same codebase
- What works that's similar to what's broken?

**Action:** Use `search_files` to find comparable patterns:

```python
search_files("similar_pattern", path="src/", file_glob="*.py")
```

### 2. Compare Against References

- If implementing a pattern, read the reference implementation COMPLETELY
- Don't skim — read every line
- Understand the pattern fully before applying

### 3. Identify Differences

- What's different between working and broken?
- List every difference, however small
- Don't assume "that can't matter"

### 4. Understand Dependencies

- What other components does this need?
- What settings, config, environment?
- What assumptions does it make?

---

## Phase 3: Hypothesis and Testing

**Scientific method:**

### 1. Form a Single Hypothesis

- State clearly: "I think X is the root cause because Y"
- Write it down
- Be specific, not vague

### 2. Test Minimally

- Make the SMALLEST possible change to test the hypothesis
- One variable at a time
- Don't fix multiple things at once

### 3. Verify Before Continuing

- Did it work? → Phase 4
- Didn't work? → Form NEW hypothesis
- DON'T add more fixes on top

### 4. When You Don't Know

- Say "I don't understand X"
- Don't pretend to know
- Ask the user for help
- Research more

---

## Phase 4: Implementation

**Fix the root cause, not the symptom:**

### 1. Create Failing Test Case

- Simplest possible reproduction
- Automated test if possible
- MUST have before fixing
- Use the `test-driven-development` skill

### 2. Implement Single Fix

- Address the root cause identified
- ONE change at a time
- No "while I'm here" improvements
- No bundled refactoring

### 3. Verify Fix

```bash
# Run the specific regression test
pytest tests/test_module.py::test_regression -v

# Run full suite — no regressions
pytest tests/ -q
```

### 3a. Go refactor compile-failure loop guard

When splitting large Go files into smaller files during a refactor and compile errors start cascading:
- Inspect the package directory for already-existing split files before generating new ones; duplicate methods/functions are common after partial refactors.
- Remember that Go package membership is directory-based: files in a subdirectory such as `apis/` are a different package/import path, not a way to organize same-package methods.
- For plugin-owned migrations, prefer embedding migration files in the owning plugin package (`//go:embed migrations/*.sql`) and registering SQL text with the core migration registry; avoid a central app-level migration embed once migrations move under plugins.
- After any automated file split, run `gofmt` first, then one targeted `go test ./...`; if the same command fails repeatedly, stop and inspect the exact named files/functions rather than rerunning unchanged.

### 4. If Fix Doesn't Work — The Rule of Three

- **STOP.**
- Count: How many fixes have you tried?
- If < 3: Return to Phase 1, re-analyze with new information
- **If ≥ 3: STOP and question the architecture (step 5 below)**
- DON'T attempt Fix #4 without architectural discussion

### 5. If 3+ Fixes Failed: Question Architecture

**Pattern indicating an architectural problem:**
- Each fix reveals new shared state/coupling in a different place
- Fixes require "massive refactoring" to implement
- Each fix creates new symptoms elsewhere

**STOP and question fundamentals:**
- Is this pattern fundamentally sound?
- Are we "sticking with it through sheer inertia"?
- Should we refactor the architecture vs. continue fixing symptoms?

**Discuss with the user before attempting more fixes.**

This is NOT a failed hypothesis — this is a wrong architecture.

---

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals a new problem in a different place**

**ALL of these mean: STOP. Return to Phase 1.**

**If 3+ fixes failed:** Question the architecture (Phase 4 step 5).

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern, don't fix again. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence, trace data flow | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare, identify differences | Know what's different |
| **3. Hypothesis** | Form theory, test minimally, one variable at a time | Confirmed or new hypothesis |
| **4. Implementation** | Create regression test, fix root cause, verify | Bug resolved, all tests pass |

## Hermes Agent Integration

### Investigation Tools

Use these Hermes tools during Phase 1:

- **`search_files`** — Find error strings, trace function calls, locate patterns
- **`read_file`** — Read source code with line numbers for precise analysis
- **`terminal`** — Run tests, check git history, reproduce bugs
- **`web_search`/`web_extract`** — Research error messages, library docs

### With delegate_task

For complex multi-component debugging, dispatch investigation subagents:

```python
delegate_task(
    goal="Investigate why [specific test/behavior] fails",
    context="""
    Follow systematic-debugging skill:
    1. Read the error message carefully
    2. Reproduce the issue
    3. Trace the data flow to find root cause
    4. Report findings — do NOT fix yet

    Error: [paste full error]
    File: [path to failing code]
    Test command: [exact command]
    """,
    toolsets=['terminal', 'file']
)
```

### With test-driven-development

When fixing bugs:
1. Write a test that reproduces the bug (RED)
2. Debug systematically to find root cause
3. Fix the root cause (GREEN)
4. The test proves the fix and prevents regression

## Real-World Impact

From debugging sessions:
- Systematic approach: 15-30 minutes to fix
- Random fixes approach: 2-3 hours of thrashing
- First-time fix rate: 95% vs 40%
- New bugs introduced: Near zero vs common

**No shortcuts. No guessing. Systematic always wins.**
