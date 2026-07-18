---
name: socialzen
description: Maintain, deploy, and debug the SocialZen social-media scheduling app (Go + React, Instagram/Facebook/Threads publishing).
---

# SocialZen Project

## Feature workflows

- See `references/quota-crop-analytics-regressions.md` when historical published posts bypass a new quota ledger, Create Post crop Apply closes without adding the active image, or analytics insight cards lose legacy/media URL thumbnails. It covers dual-path idempotent quota backfill, image-vs-video queue semantics, `NULLIF` media fallback, focused regression tests, and deployment checks.
- See `references/analytics-issues-7-11-implementation.md` when implementing the analytics follow-up covering nullable/unavailable metrics, soft-disconnecting referenced accounts, honest success/partial/failure refresh outcomes, Top Posts ranking, and clickable What Worked references. It includes focused tests, deployment bundle checks, and scoped-commit guidance for a dirty working tree.
- See `references/analytics-consistency-review.md` when reviewing or implementing Analytics ranking, thumbnail propagation, unavailable-vs-zero semantics, post-derived trend buckets, refresh-count meaning, or What Worked. It defines the one-source-of-truth contract and the weekly-bucket pitfall.
- See `references/user-friendly-multiplatform-publishing-errors.md` when provider errors must be normalized into safe codes/messages/actions across Posts, Calendar, Post Detail, and Edit & Retry; it covers raw-log-only diagnostics, per-target status, partial success, and backend-enforced recoverable retry.
- See `references/media-edit-google-auth-fixes.md` when visible video trim handles, Create Post crop-queue duplication, per-item replacement-media removal, or concurrent Google GIS sign-in attempts regress. It includes the minimal interaction invariants, focused tests, backend no-op check, and deploy verification.
- See `references/duplicate-countdown-refresh-details-mobile-crop.md` when duplicate scheduling loses the selected countdown, analytics partial success hides per-target outcomes, or the mobile photo cropper clips the image beside a fixed right menu. It covers request-body preservation, detail formatting, scoped touch handling, responsive stacking, tests, and deploy checks.
- See `references/edit-retry-existing-media-controls.md` when existing Edit / Edit & Retry photos or videos are blank, non-clickable, lack an × control, or editing/removing one carousel item drops unaffected siblings. It covers media-type-aware editor routing/rendering, replacement payload preservation, focused tests, and deployed-bundle verification.

## Architecture

- **Backend**: Go (single binary, `apps/backend-go/`)
- **Frontend**: React + Vite + TypeScript (`apps/frontend/`)
- **Database**: SQLite at `/opt/socialzen/data/socialzen.db`
- **Service**: `systemctl` unit `socialzen.service`, runs from `/opt/socialzen/`
- **Nginx**: Serves frontend from `/var/www/html/projects/socialzen/` (alias, NOT `/var/www/socialzen/`), proxies API to `:8089`. Cloudflare CDN in front with 4-hour cache.
- **Public**: https://socialzen.ahsanworks.com/projects/socialzen/

### Key backend packages

| Package | Role |
|---------|------|
| `internal/posts` | CRUD, publishing pipeline, enqueue cron |
| `internal/comments` | Instagram comment sync via Graph API |
| `internal/facebook` | Facebook Page publishing (feed/photos/videos) |
| `internal/sync` | Metrics sync (likes, reach, impressions) |
| `internal/models` | DB helpers, user auth, app config |

### Key files

| File | What |
|------|------|
| `main.go` | Server setup, routes, 1-min publishing cron |
| `instagram_oauth.go` | OAuth for IG/FB/Threads, scopes, token exchange |
| `db.go` | Schema (posts, post_targets, instagram_accounts, facebook_pages, threads_accounts) |
| `internal/posts/publisher.go` | Publishing loop, per-platform dispatch |
| `internal/posts/handler.go` | HTTP handlers for post CRUD, enqueue, duplication |
| `internal/comments/handler.go` | Comment CRUD, Instagram comment push/pull |
| `internal/comments/sync.go` | Comment sync from Instagram API |
| `internal/comments/instagram.go` | Instagram media metrics, insights, comment operations |

## Publishing Flow

1. **Cron** (every 60s, started in `main.go`): runs `publishDuePosts()`
2. **Enqueue**: `UPDATE posts SET status='PUBLISHING' WHERE status='SCHEDULED' AND publish_at <= now() + 5min`
3. **Publish cycle**: For each PUBLISHING post, iterate its PUBLISHING targets
4. **Per-platform**: `publishToPlatform()` dispatches to `facebook.PublishTextPost/PhotoPost/VideoPost/LinkPost` or `publishInstagramImage()`
5. **Result**: Success → target set to PUBLISHED with `platform_post_id`. Failure → target set to FAILED with `error_message`.
6. **Post status**: All targets OK → PUBLISHED. Any failed → FAILED. For already-published targets + new failed ones, uses `SELECT COUNT(*)` to determine partial success.

## Post Analytics Schema

The `posts` table tracks these metrics per post:

| Column | Source | Description |
|--------|--------|-------------|
| `likes` | `RefreshPostMetrics()` → IG `/media` | Like count |
| `comments` | `RefreshPostMetrics()` → IG `/media` | Comment count |
| `reach` | `RefreshPostInsights()` → IG `/insights` | Unique viewers |
| `impressions` | `RefreshPostInsights()` → IG `/insights` | Total views |
| `saves` | `RefreshPostInsights()` → IG `/insights` | Saved/bookmarked |
| `shares` | `RefreshPostInsights()` → IG `/insights` | Reposts/shares |

**Engagement Rate** = `(likes + comments + saves + shares) ÷ reach × 100%`

Both `analyticsRefresh` and the Sync button call `RefreshPostMetrics` + `RefreshPostInsights` to pull real data from Instagram's Graph API.

- Frontend gate: `post.status !== "SCHEDULED" && post.status !== "FAILED"` blocks non-editable posts
- Backend PATCH: When a FAILED post is edited, resets post to SCHEDULED and all FAILED targets to SCHEDULED (PUBLISHED targets stay untouched)
- The enqueue cron then picks it up on the next minute

## Deploy

```bash
cd /home/ubuntu/socialzen/apps/backend-go
go build -o /tmp/socialzen-api .
sudo install -m 755 /tmp/socialzen-api /opt/socialzen/socialzen-server
sudo systemctl restart socialzen.service

# Frontend (if changed):
cd /home/ubuntu/socialzen/apps/frontend
pnpm build
sudo rsync -a --delete dist/ /var/www/html/projects/socialzen/
sudo chown -R www-data:www-data /var/www/html/projects/socialzen
```

Verify: `systemctl is-active socialzen.service && curl -sI http://localhost/projects/socialzen/ | head -1`

After deploy, also verify Cloudflare isn't serving stale SPA fallback for JS:
```bash
# JS asset should return application/javascript, NOT text/html
curl -sI "https://socialzen.ahsanworks.com/projects/socialzen/assets/$(basename $(ls /var/www/html/projects/socialzen/assets/index-*.js | head -1))" 2>&1 | grep content-type
# Expected: content-type: application/javascript
```

After deploy, commit + push from `/home/ubuntu/socialzen`.

## Facebook Page Publishing Scope

Facebook Page publishing (`POST /{page-id}/feed`, `/photos`, `/videos`) requires `pages_manage_posts` + `pages_read_engagement` on the Page token, but **do not request `pages_manage_posts` in OAuth unless the Meta app has App Review / Advanced Access for that permission**. Meta rejects the whole connect flow with `Invalid Scopes: pages_manage_posts` when the app is not approved.

Current safe connect scopes: `pages_show_list`, `pages_read_engagement`, `business_management`.

If the user reports `Invalid Scopes: pages_manage_posts`, remove `pages_manage_posts` from `facebookScopes` in `instagram_oauth.go`, rebuild/deploy the backend, and verify `/api/facebook/oauth/start` returns an auth URL whose `scope=` omits it. Use an existing regression test (or add the smallest targeted one) that fails if `pages_manage_posts` appears in the Facebook OAuth URL.

If Facebook publishing later fails with a 403 mentioning `pages_manage_posts`, that is a product/app-review issue, not a reconnect-flow bug: get the permission approved in Meta first, then intentionally re-add it and reconnect Facebook in Settings → Accounts so saved Page tokens receive the new scope. Diagnose this from `journalctl -u socialzen.service` even if current `post_targets` no longer contain Facebook rows; users may have deleted failed posts, but the provider rejection remains in historical logs. See `references/facebook-scope-errors.md` for historical error transcripts.

When the user says Meta approval is done and still reports the same 403, treat it as authorization to re-enable Facebook Page publishing in code: add `pages_manage_posts` to `facebookScopes` in `instagram_oauth.go`, update the OAuth regression test to require that scope, run the targeted Facebook OAuth test plus `go build`, deploy the backend, and verify `/api/facebook/oauth/start` includes `pages_manage_posts`. Tell the user to reconnect Facebook again after deployment because old Page tokens will not gain the new scope automatically.

If the user says Meta approval is done and they already reconnected but publishing still fails with `(#200) Permissions error` or the long message requiring `pages_read_engagement` + `pages_manage_posts`, first check the currently deployed `facebookScopes` and recent `journalctl` lines. If `pages_manage_posts` is still absent from `facebookScopes`, reconnect cannot grant it; report that approval must be followed by a deliberate code/config change to request `pages_manage_posts`, deploy, then reconnect. Do not claim reconnect is enough, and do not add the scope until approval/Advanced Access is confirmed because unapproved apps can break OAuth with `Invalid Scopes`.

## Debugging

### Check cron cycles
```bash
journalctl -u socialzen.service --since "10 minutes ago" --no-pager | grep 'publish cycle'
```

### Check failed posts + targets
```bash
sqlite3 /opt/socialzen/data/socialzen.db "
SELECT p.id, p.status, p.type, p.error_message,
  GROUP_CONCAT(pt.platform||':'||pt.status||':'||COALESCE(pt.error_message,''),' | ') AS targets
FROM posts p
LEFT JOIN post_targets pt ON pt.post_id=p.id
WHERE p.status='FAILED'
GROUP BY p.id ORDER BY p.updated_at DESC LIMIT 10;
"
```

### Check connected accounts
```bash
sqlite3 /opt/socialzen/data/socialzen.db "
SELECT id, ig_user_id, ig_username, provider,
  CASE WHEN access_token_encrypted IS NOT NULL THEN 'has_token' ELSE 'no_token' END
FROM instagram_accounts;
"
```

```bash
sqlite3 /opt/socialzen/data/socialzen.db "
SELECT id, page_id, page_name, status, token_expires_at FROM facebook_pages;
"
```

### Check if a published post has platform_post_id (needed for metrics/comments)
```bash
sqlite3 /opt/socialzen/data/socialzen.db "
SELECT pt.post_id, pt.platform, pt.status, pt.platform_post_id, pt.platform_permalink
FROM post_targets pt WHERE pt.status='PUBLISHED' ORDER BY pt.updated_at DESC LIMIT 10;
"
```

### Check billing/post counts for current month

When adding short-lived/test subscription plans, keep plan metadata, Xendit invoice amount lookup, `current_period_end`, subscription status identity, and frontend plan ordering in sync. See `references/subscription-one-minute-plans.md`.

When a short-lived plan reaches `current_period_end` but still appears active, fix expiry in `models.SubscriptionData()` and add a global app banner that re-checks at period end. See `references/subscription-expiry-status-and-banner.md`.

When a user says subscription cancellation is still `active` after clicking cancel, distinguish paid access from renewal intent. The correct state is still `status: "active"` until `current_period_end`, plus persisted `cancel_at_period_end=1`; cancel must clear pending invoices, remove the cancel button, return `cancelAtPeriodEnd` from `SubscriptionData()`, and suppress renewal/continuation popups. When the canceled period ends, return the user to the free tier. See `references/subscription-cancel-renewal-state.md`.

When a user downgrades before the current period expires and Xendit registers an invoice, keep the current active plan unchanged but persist the pending downgrade invoice and surface a global reminder with Continue/Reject actions. See `references/subscription-pending-downgrade-invoice.md`.

When the unpaid invoice reminder is too subtle, keep persistence backed by `pendingPlanChange` and render the reminder as a fixed decision card: bottom-right on desktop/tablet, centered on mobile. See `references/subscription-pending-invoice-popup-ux.md`.

```bash
sqlite3 /opt/socialzen/data/socialzen.db "
SELECT 
  (SELECT COUNT(*) FROM posts WHERE status='SCHEDULED' AND publish_at>='$(date +%Y-%m)-01' AND publish_at<'$(date -d 'next month' +%Y-%m)-01') as scheduled,
  (SELECT COUNT(*) FROM posts WHERE status='PUBLISHED' AND publish_at>='$(date +%Y-%m)-01' AND publish_at<'$(date -d 'next month' +%Y-%m)-01') as published,
  (SELECT COUNT(*) FROM posts WHERE status='FAILED' AND publish_at>='$(date +%Y-%m)-01' AND publish_at<'$(date -d 'next month' +%Y-%m)-01') as failed,
  (SELECT COUNT(*) FROM posts WHERE publish_at>='$(date +%Y-%m)-01' AND publish_at<'$(date -d 'next month' +%Y-%m)-01') as total;
"
# FAILED posts are NOT counted in billing (neither scheduled nor published). Only PUBLISHED counts.
```

### Login says "Request timed out"

First prove whether this is really the user's connection or a backend hang. Check health, then POST directly to the login endpoint from localhost with known demo credentials and a timeout:
```bash
systemctl is-active socialzen.service && curl -sS -m 5 -w '\nHTTP %{http_code} total=%{time_total}s\n' http://127.0.0.1:8089/health
curl -sS -m 20 -w '\nHTTP %{http_code} total=%{time_total}s\n' \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@brandorganizer.local","password":"password123"}' \
  http://127.0.0.1:8089/api/auth/sign-in/email
```

If `/health` is instant but `/api/auth/sign-in/email` times out with zero bytes, it is not the user's internet connection. Treat it as a backend DB/login hang: inspect `auth.go` (`userByEmail`, `createSession`) and any live SQLite lock/deadlock symptoms before touching the frontend. Also test an invalid email/password — if both valid and invalid login hang, the block is likely before password validation or while acquiring the DB connection.

### Posts list is empty but DB has posts (silent SQL error)

```bash
# 1. Check raw posts exist for user
sudo sqlite3 /opt/socialzen/data/socialzen.db "SELECT COUNT(*) FROM posts WHERE user_id='<user_id>';"

# 2. Run the exact FetchPosts query manually
sudo sqlite3 /opt/socialzen/data/socialzen.db "SELECT p.id,p.type,p.status,p.publish_at FROM posts p LEFT JOIN instagram_accounts a ON a.id=p.instagram_account_id WHERE p.user_id='<user_id>' ORDER BY p.publish_at DESC LIMIT 5;"

# 3. If step 1 works but step 2 fails, compare SELECT columns against schema
sudo sqlite3 /opt/socialzen/data/socialzen.db ".schema posts" | tr ',' '\n' | grep -i shares

# 4. If column is missing, the migration ran on a different migration path.
#    Add ALTER TABLE to models.Migrate() and apply manually.
```

### Run specific tests
```bash
cd apps/backend-go && go test ./internal/posts ./internal/comments
```

## Pitfalls

- **Edit & Retry media cancel must restore previous media**: In `EditPostPage.tsx`, selecting replacement media can set `mediaMode="replace"` before upload/crop completes. Crop Cancel/X/outside-card click and the explicit cancel button must route through one “use previous media” action that restores `mediaMode="keep"`, clears `newMedia`, and clears upload/input progress. Cancel must never upload and must not leave the form in replace mode with empty media. Use the requested button copy `Cancel and use previous media.` under Change media. See `references/edit-retry-media-cancel-previous-media.md`.

- **Story publishing plan should not add feature flags when Meta scopes are already approved**: For SocialZen story-posting plans, do not propose `instagram_story_auto_publish` / `facebook_story_auto_publish` feature flags just because Meta endpoints need live verification. The user's workflow is to implement against approved Meta Developer scopes and test publishing in real time after implementation. Keep the launch-risk language focused on live Graph API proof, endpoint availability, user-visible errors, and fallback/manual package behavior — not an app-level feature flag gate.

- **Story post scheduling implementation**: Treat `STORY` as a first-class post type, keep the existing scheduled-post lifecycle, use Instagram `media_type=STORIES` with `image_url` vs `video_url` based on actual media type, use the longer Reel/video container timeout, and make Facebook Story targets fail clearly as manual-required until endpoint proof exists. See `references/story-post-scheduling-implementation.md`.

- **SocialZen plans/review docs must be published as public HTML before implementation**: When producing a SocialZen plan, PRD, or review artifact, save the canonical source under `/home/ubuntu/socialzen/.hermes/plans/` or `/home/ubuntu/socialzen/docs/`, create a standalone dark-theme responsive HTML artifact with a light/dark toggle under `/home/ubuntu/socialzen/docs/<slug>.html`, publish it via `/usr/share/nginx/html/prds/socialzen/<slug>.html`, and verify both local and public URLs. Use `https://socialzen.ahsanworks.com/prd/socialzen/<slug>.html`, not a raw IP or the live app route. If the first publish returns 404, do not assume nginx is wrong; ensure the destination directory exists and install the file with sudo (`sudo mkdir -p /usr/share/nginx/html/prds/socialzen && sudo cp docs/<slug>.html /usr/share/nginx/html/prds/socialzen/<slug>.html && sudo chmod 644 ...`) before re-checking `curl -sI http://localhost/prd/socialzen/<slug>.html | head -1`. For a new SocialZen feature request, do this planning/review artifact first even if the user's wording sounds implementation-oriented (for example "improve" or "add"); stop after the public plan and explicitly state that implementation/deployment has not happened unless the user clearly asked to skip review or to implement from an already-approved plan.

- **PRD/review HTML feedback should be patched and redeployed immediately**: When the user gives review feedback on a deployed PRD/review HTML file, update the source under `/home/ubuntu/socialzen/docs/`, copy/symlink it to `/usr/share/nginx/html/prds/socialzen/`, and verify with `curl -sI http://localhost/prd/socialzen/<file>.html | head -1`. Return the public `/prd/socialzen/...` link with a bumped cache-buster query.

- **Calendar busy-day UX should reuse monthly data and preserve drag/drop**: If many posts on one date make the month grid hard to scan, add a selected-day scrollable dialog/list from the already-loaded monthly `posts` state instead of reaching for a backend change. The day popup should be wide enough for card-style rows (around `w-[min(94vw,980px)] max-w-none`) and the list body should scroll (`overflow-y-auto`, roughly `max-h-[min(76vh,760px)]`) so dates with more than 3 posts reveal the rest by scrolling. User-facing calendar post clicks should open this day list first, not jump straight to post detail; detail can remain accessible from inside the list. Use a date-number/`View all` click target, not the whole droppable cell, so `useDroppable` day cells and `useDraggable` post cards keep rescheduling behavior. See `references/calendar-day-post-list-ux.md`.

- **Generic publish failure hides real cause**: Do not set parent `posts.error_message` to only "Some platforms failed to publish" / "All platforms failed to publish". Aggregate failed `post_targets.error_message` values into platform-specific parent copy so the PostCard shows an actionable reason. See `references/publish-failure-error-surfacing.md`.

- **Facebook-only posts misclassified as cross-platform by post-target backfill**: Keep every post-target backfill guarded with `WHERE NOT EXISTS (SELECT 1 FROM post_targets pt WHERE pt.post_id=p.id)`. SocialZen has legacy/test migration paths in `apps/backend-go/db.go` in addition to production `internal/models.Migrate()`; if those paths backfill Instagram targets for all posts, a Facebook-only post can later receive an extra Instagram target and be treated as cross-platform. Regression check: create `platforms:["facebook"]` + `facebookPageId`, then assert zero Instagram targets and one Facebook target in `post_targets`.

- **User may see old frontend after deploy**: The JS bundle filename changes (hash), but browser may cache the old HTML. User needs a hard refresh (Ctrl+Shift+R).
- **Cloudflare SPA fallback caching**: If frontend is deployed to the WRONG directory (or before rsync finishes), nginx's `try_files` falls through to `index.html` for JS/CSS requests. Cloudflare caches that HTML as the JS file (`content-type: text/html`, `cf-cache-status: HIT`), breaking the entire app until the Cloudflare cache expires (4-hour `max-age`). Verify with: `curl -sI "https://socialzen.ahsanworks.com/projects/socialzen/assets/<some-file>.js" | grep content-type`. If it returns `text/html` instead of `application/javascript`, deploy to the correct path and wait for cache expiry or purge Cloudflare.
- **Facebook reconnect needed after scope change**: If Facebook scopes change, existing connections don't get the new scope. User must reconnect in Settings → Accounts.
- **Instagram account disconnect**: If a post's `instagram_account_id` points to a deleted account, publishing fails with "Instagram account not connected." The user needs to reconnect Instagram.
- **Threads OAuth saves to wrong table**: Without explicit Threads handling, Threads accounts were saved to `instagram_accounts` instead of `threads_accounts`. Fixed in `instagram_oauth.go` — Threads callback now inserts into `threads_accounts` with correct schema and performs long-lived token exchange via `th_exchange_token`.
- **Settings active-tab theming**: The Settings page has a secondary left nav (`apps/frontend/src/pages/settings/SettingsPage.tsx`) beside the main sidebar. Its active state should match the sidebar's active purple pill. Use Tailwind tokens `bg-primary text-primary-foreground`; avoid `bg-[var(--ink)] text-white`, which renders as a black/white selected tab and looks inconsistent in dark mode.

- **Settings theme toggle and back behavior**: Authenticated theme controls belong only in Settings → Accessibility; visitor theme controls stay on the Landing Page. Do not import `ThemeToggle` into authenticated global chrome like `Topbar`. Settings subpage Back should navigate to `/app/settings` with `{ replace: true }` so hub Back returns to the page that opened Settings, not back into the subpage. See `references/settings-navigation-theme-and-back-behavior.md`.

- **Desktop Settings section switching must use route navigation, not only query params**: `SettingsPage.tsx` derives `activeTab` from `pathSection` before `?tab=`. On desktop, if the app is currently at `/app/settings/profile` (or any `/app/settings/:section`) and the sidebar only calls `setSearchParams({ tab })`, `pathSection` keeps winning and the user cannot switch to Billing/Accounts/etc. Fix sidebar changes with `navigate(`/app/settings/${section}`)` and remove unused `setSearchParams` in the page-level Settings component. Keep the existing OAuth callback query cleanup inside `InstagramAccountsTab` unchanged.

- **Settings account connection flow should gate OAuth inline**: For Settings → Connected accounts UX changes, keep OAuth/API helpers unchanged (`startInstagramConnect`, `startFacebookOAuth`, `startThreadsOAuth`) and add the pre-OAuth requirements step in the frontend card state. Use one `platformConnectionConfig` for platform copy, requirements, notes, benefits, labels, and icons; render shared announcement/connected/empty cards instead of duplicating three platform JSX blocks. The first click should show requirements inline; only the `Continue to <Platform>` action should start OAuth. Add a small test around the config/gating copy, run `pnpm exec vitest run src/pages/settings/SettingsPage.test.tsx`, `pnpm typecheck`, and `pnpm build`. After deploy, grep the deployed `SettingsPage-*.js` bundle for distinctive new copy so Cloudflare/browser cache does not hide a stale build.

- **New Post account selection should be explicit and hide internal IDs**: On `CreatePostPage.tsx`, no connected platforms should show `Please connect at least one platform before creating a post.`, reuse existing connect helpers, and disable platform/Post/Schedule controls. With connected accounts, start with `platforms=[]`; do not auto-select a single Instagram account. Enable account selectors only after a platform is checked, clear selected account/page when unchecked, render avatar/icon + platform + username/page name, and never show `acct_*` IDs. Instagram selector rows must be direct `provider === "instagram"` only — do not include `mock` or Facebook-derived rows, because that makes Instagram appear connected without explicit consent. If the Select trigger shows `acct_*`, pass an explicit selected label to `SelectValue` from the selected account. Keep backend payload/business logic unchanged unless requested. See `references/new-post-account-selection-ux.md`, `references/new-post-provider-filter-and-select-label.md`, and `references/platform-connection-guardrails.md`.

- **Platform connection guardrails must be platform-specific and live-refresh after OAuth**: When New Post/Edit Retry platform availability changes, derive connection state from live Instagram/Facebook API data, refresh on window focus after OAuth, render disconnected platform chips with a subtle overlay plus `Connect your <Platform> account to enable posting.`, and block failed-post retry based on original `post.targets` until every required platform is reconnected. Backend retry validation should still enforce same external provider account/page via `resolveFailedTargets()`, not merely any same-platform connection. See `references/platform-connection-guardrails.md`.

- **New Post responsive/design regressions after mockup changes**: `CreatePostPage.tsx` is rendered inside `AppLayout` with the desktop sidebar and mobile bottom nav. Do not replace it with a standalone full-screen dark card/mockup unless the user explicitly asks for a separate page shell; that can make the route mismatch the app and break responsiveness. Prefer the app-native route shape (`Topbar`, `p-4 md:p-8 max-w-[640px]`, theme tokens, normal form-flow actions) and preserve the direct-Instagram/account-label fixes when reverting. See `references/new-post-responsive-design-regression.md`.

- **Instagram disconnect must prove the row is gone**: If Instagram appears connected again after refresh, do not stop at frontend `platforms=[]` fixes. Check the live `instagram_accounts` row for the user, make `DELETE /api/instagram/accounts/:id` fail when no row was actually deleted (`RowsAffected()==0`), keep Settings/New Post direct-Instagram-only (`provider === "instagram"`), and clean up stale rows only after identifying the affected user. Use styled platform icons/SVGs instead of emoji placeholders in the New Post platform/account UI. See `references/instagram-disconnect-consent-persistence.md`.

- **Dark mode white-on-white text**: Components that use `background: "#fff"` (hardcoded white) with `color: "var(--ink)"` become invisible in dark mode because `--ink` resolves to `#f7f2ff` (near-white). Preferred fix: use CSS variables — `var(--card)` for card/input backgrounds, `var(--bg)` for page backgrounds. Check these files: PostCard.tsx, CreatePostPage.tsx, EditPostPage.tsx, PostsPage.tsx, DashboardPage.tsx.

  **CRITICAL**: React's `style={{ background: "#fff" }}` renders to the DOM as `style="background: rgb(255, 255, 255)"` — NOT as a hex string. CSS attribute selectors targeting `#fff` or `#ffffff` will NEVER match React inline styles. You MUST include `rgb()` patterns. The `globals.css` fallback below covers all known renderings:

  ```css
  /* React renders #fff as rgb(255,255,255) in the DOM — rgb() patterns are MANDATORY */
  .dark [style*="rgb(255, 255, 255)"],
  .dark [style*="rgb(255,255,255)"],
  .dark [style*="rgba(255, 255, 255"],
  .dark [style*="rgba(255,255,255"],
  .dark [style*="background: #fff"],
  .dark [style*="background:#fff"],
  .dark [style*="background: white"],
  .dark [style*="background:white"],
  .dark [style*="background-color: white"],
  .dark [style*="background-color:white"] {
    background: var(--card) !important;
  }
  ```

  **Verification**: after deploying a CSS change, `curl` the production CSS and grep for the new patterns — if `rgb(255` returns 0 matches the fix won't work:
  ```bash
  curl -s "https://socialzen.ahsanworks.com/.../index-*.css" | grep -c 'rgb(255'
  # MUST return >= 1. If 0, the build didn't pick up globals.css changes.
  ```

  **Pitfall: fallback selectors can overmatch intentional white UI controls.** Photo/video crop controls sit on black media previews, so their white handles must stay white in dark mode. The global `.dark [style*="rgb(255..."]` fallback will turn those handles into `var(--card)` and make them low-contrast. Fix deliberate white-on-black controls by using off-white `rgb(254,254,254)` or a scoped exception, and leave a `ponytail:` comment explaining that it intentionally evades the broad fallback.

  **Also check related dark-mode tokens:** `CalendarGrid.tsx` uses `var(--surface)` for off-month calendar cells; keep `--surface` defined in both `:root` and `.dark`. Hardcoded light alert fills such as `#fef2f2`, `#fef3c7`, and `#fffbeb` need dark-mode fallback selectors in `globals.css` so error/warning banners don't glow in night mode.
- **Comment GET blocks the response**: In `internal/comments/handler.go`, `syncInstagramComments()` was called synchronously on GET, making HTTP calls to Instagram's API (1-5s) before returning the comment list. MUST run as `go h.syncInstagramComments(...)` — the sync fetches from Instagram in the background while the local DB result is returned immediately. Because GET now returns cached local rows first, the frontend comment list should do one short delayed refresh after opening so newly-synced Instagram comments appear without requiring the user to close/reopen.
- **Open comment drawer can look stale while Instagram comments arrive**: `CommentList.tsx` should not rely only on the initial GET + one delayed refresh. While the comments drawer/modal is open, poll the local comments endpoint lightly (for example every 10s) so provider comments synced by background GETs appear without closing/reopening. Keep this scoped to the open drawer; do not add global polling.
- **Replies saved but invisible because threads stay collapsed**: If replying through the project UI stores the row but the user says the reply text does not appear, inspect `CommentList.tsx` before changing backend sync. Replies can be present in `comment.replies` but hidden because `showReplies` defaults to `false`. Initialize/auto-set expanded state when `comment.replies.length > 0`, especially after `onReplyAdded()` reloads the comment list.
- **Instagram comment sync can hide replies under duplicate parents**: If a local top-level comment was posted to Instagram, its row has a local ID (`comment_*`) plus `instagram_comment_id`. Later provider sync must upsert by existing `(user_id, media_id, instagram_comment_id)` and reuse that local ID before inserting `igcomment_<provider-id>`. Otherwise synced replies attach to the duplicate `igcomment_*` parent and are not visible under the comment the user sees. Regression shape: create local parent with `instagram_comment_id='ig_parent'`, sync IG response with nested reply, assert reply `parent_id` remains the local parent ID and only one row exists for `ig_parent`.
- **Comment/reply sync depends on provider IDs at two levels**: When comments/replies publish to Meta but do not display, first inspect `post_targets.platform_post_id` and `instagram_comments.instagram_comment_id`. Top-level sync cannot start without the post's provider media ID; reply publish/sync also needs the parent comment's provider ID. Async publish can leave local rows with missing provider IDs unless errors are logged/surfaced. See `references/comment-sync-provider-id-and-reply-mapping.md` for RCA queries, failure points, logging checklist, and regression shape.
- **Comment missing triage must prove counts at every layer before fixes**: For Instagram/Facebook comments missing from UI, trace Meta API → sync → DB → API response → frontend receive → UI render with explicit top-level/reply counts. If DB rows exist but `/api/instagram/comments/:postId` returns zero bytes or times out, suspect the API response layer, especially a SQLite `SetMaxOpenConns(1)` self-deadlock from calling `isLiked()`/`fetchReplies()` while the top-level `Rows` cursor is still open. Separately report Meta returning `data:[]` as a provider/token/scope/API-host issue; do not conflate it with UI rendering. See `references/comment-data-flow-count-triage.md`.
- **Meta comments and replies must paginate separately**: Do not rely on embedded Instagram `replies{...}` or a single comments response. Facebook and Instagram top-level comments use cursor pagination, and replies require their own paginated edge (`/{ig-comment-id}/replies` for Instagram, `/{comment-id}/comments` for Facebook). Upsert the provider parent first by `(user_id, media_id, instagram_comment_id)` so reply rows attach to the visible local parent. See `references/meta-comment-pagination-audit.md` for the compact audit/fix pattern and fake-Graph regression shape.
- **Analytics includes non-published posts**: `analyticsOverview` passed ALL posts (SCHEDULED, FAILED, DRAFT) to `analyticsSummary()`, dragging averages to zero. Fix: filter to `status == "PUBLISHED"` before computing aggregates. Also, `analyticsRefresh` should call `comments.RefreshPostInsights()` (reach, impressions, saves) in addition to `RefreshPostMetrics()` (likes, comments).

- **Provider analytics must use exact `post_targets` identity and target-level storage**: Shared `posts` metric columns cannot safely represent cross-platform posts. Store current metrics in `post_target_metrics`, preserve unsupported values as `NULL`, and pass the exact `post_target_id` through every provider refresher—passing only `post_id` can repeatedly update the newest same-platform target while falsely reporting all targets successful. Wire provider refresh anywhere analytics refresh occurs, close `Rows` before nested DB/API work under `SetMaxOpenConns(1)`, and treat provider/JSON failures as failures rather than persisting zero. Facebook has no Instagram-style saves; Threads maps replies→comments, views→reach/impressions fallback, and reposts+quotes→shares. See `references/provider-safe-analytics-implementation.md`.

- **Analytics filtering and All Platforms aggregation must share one backend source of truth**: Validate inclusive local-calendar `from`/`to`, `platform`, and `account_id` on the backend. Query target metrics, but group All Platforms post DTOs back by parent post ID so post count, averages, comparisons, and What Worked are not duplicated once per target. Return backend-built daily/weekly `trendBuckets` including derived engagement, and keep the frontend response key exact so it does not silently rebuild per-post trends. Cards/chart/table/insights/PDF must derive from the same filtered result. Label All Platforms as summed activity, not unique people. See `references/provider-safe-analytics-implementation.md`.

- **Top Posts card filter/search should stay UI-local when requested**: If the user asks to update only the `Top Posts by Total Engagement` card filter UI, keep the backend and global overview/chart data unchanged. Put the platform dropdown + caption search inside `components/analytics/TopPostsTable.tsx`, reuse `postMatchesPlatforms()` via a shared helper (for example `filterAnalyticsPosts(posts, platform, search)` in `lib/analytics.ts`), apply platform first, then `search.trim().toLowerCase()` against `post.caption ?? ''`, and render `No posts found` inside the card when local filtering empties the table. If testing only this helper, run the direct Vitest binary (`pnpm exec vitest run src/lib/analytics.test.ts`); `pnpm test -- src/lib/analytics.test.ts` may still discover unrelated flaky tests in this repo.
- **Posts page filters can hide newly-created posts if backend ignores query params**: The Posts page sends `status`, `account_id`, `search`, `limit`, and `offset` to `/api/posts`; `ListPosts` must actually pass those into `FetchPosts`. If the user says a just-published/scheduled/failed post is absent under every filter, inspect both the POST creation result and the list query. `FetchPosts` should filter in SQL and use `LEFT JOIN instagram_accounts`, not `JOIN`, because Facebook-only or stale-Instagram-account posts can otherwise exist in `posts`/`post_targets` but vanish from every Posts page tab.
- **Dashboard placeholder card contrast**: On the Dashboard fallback cards, don't use low-opacity theme text when the card background is extreme. The lime/yellow follower placeholder needs explicit dark text (black/near-black), and the dark top-post placeholder needs explicit white text so it stays readable in both light and dark modes.
- **Delete post doesn't cascade to platforms**: The DELETE handler only removed local DB rows. Must first look up `platform_post_id` from `post_targets` for PUBLISHED targets and call the platform's DELETE API: Instagram `DELETE /{ig-user-id}/media?access_token=...`, Facebook `DELETE /{page-id}_{post-id}?access_token=...`. Then clean up `post_targets`, `instagram_comments`, and `posts`.

- **Dark mode: preset buttons with `var(--ink)` background + `#fff` text = invisible in dark mode**: In PhotoCropModal and VideoCropModal, the selected ratio-preset button uses `background: "var(--ink)"` with `color: "#fff"`. In dark mode, `--ink` = `#f7f2ff` (near-white), so white text is invisible. Fix: selected text should use `color: "var(--bg)"` (dark bg in dark mode), non-selected background should use `var(--card)` instead of hardcoded `#fff` so it picks up the dark-mode card color.

- **Photo crop image nearly invisible or crop selection becomes a solid dark block in dark mode**: Inspect `PhotoCropModal.tsx` plus `globals.css` before changing crop math. The global `.dark [style*="rgb(255..."]` / `rgba(255...)` fallback is intentionally broad and can mistake any inline style containing white—including a transparent crop-box `boxShadow: "... rgba(255,255,255,.85)"`—for a white card background. Because the fallback sets `background: var(--card) !important`, it can fill the otherwise transparent crop selection and cover the image precisely inside the blue handles. Keep the actual image preview scoped and isolated: use `.photo-crop-surface` with `isolation: isolate` and explicitly reset the child image to `filter: none !important`, `opacity: 1 !important`, and `mix-blend-mode: normal !important`. For deliberate white crop chrome, use off-white `rgb/rgba(254,254,254)` or a narrowly scoped exception so it does not match the legacy fallback. Add a small regression guard asserting the crop selection no longer contains the matching `rgba(255...)` inline style. Do not touch drag/resize/pan logic unless reproduction proves it is broken. Verify the targeted regression test, `pnpm typecheck`, `pnpm build`, grep the built `PhotoCropModal-*.js` for the off-white marker, deploy, and confirm the public JS asset returns `application/javascript`.

- **Photo crop output has a large dark/empty band after CSS visibility fixes**: Do not keep applying theme/CSS fixes if `.photo-crop-surface > img` already resets `filter`, `opacity`, and `mix-blend-mode`. Inspect the original pixels, crop box geometry, and `ctx.drawImage(...)` source rectangle. If the crop box is initialized to the full image and the source has obvious dark/transparent padding, initialize the crop box to detected visible content conservatively; leave drag/resize/pan math unchanged unless reproduction proves it is wrong. See `references/photo-crop-dark-padding.md` for the RCA checklist and detector pattern.

- **Photo crop dark/blank area after CSS fix requires layer-by-layer RCA**: If a user says the crop bug persists after hard refresh, do not apply another CSS fix first. Prove whether the dark area is in the uploaded pixels, crop rectangle/canvas output, preview rendering, or theme CSS. Check source image metadata/pixels, `ctx.drawImage` inputs, generated file pixels, preview CSS (`overflow`, `object-fit`, `transform`, `filter`, `opacity`, `mix-blend-mode`), parent containers, and light vs dark mode. If the crop selection already contains a large dark/empty region and canvas output preserves it, the root is crop geometry/content bounds, not theme CSS. If transparent PNG areas appear as a solid black/dark rectangle, inspect `offscreen.toBlob`/`new File` output type before CSS: exporting every crop as JPEG strips alpha and must be fixed by preserving PNG output. See `references/photo-crop-root-cause-triage.md` and `references/photo-crop-transparent-png-output.md`.

- **Photo crop Dark Mode reports need reproduced evidence before any fix**: When the user says previous crop fixes did not change behavior, treat the task as read-only debugging. Reproduce specifically in the Photo Crop modal with `.dark` enabled, identify the first bad layer (original upload → crop modal → crop preview → generated file → uploaded file → final preview), and provide screenshots/debug values before suggesting implementation. CDP/DataTransfer injection is a reliable path for hidden React file inputs; see `references/photo-crop-dark-mode-cdp-reproduction.md`.

- **REEL/VIDEO not supported by Instagram publisher**: `publishInstagramImage()` in `publisher.go` had a hard gate: `if post.typ != "PHOTO" && post.typ != "IMAGE" { return error }`. REEL and VIDEO types were rejected with "Instagram publishing supports images only." Fix: modify `createInstagramMediaContainer()` to accept post type — for REEL/VIDEO, send `media_type=REELS` and `video_url` to the Instagram `/media` endpoint. For PHOTO/IMAGE/CAROUSEL_ALBUM, send `image_url` as before.

- **Billing: `freePostsUsed` column never incremented**: The `free_posts_used` column on the `users` table exists and is read by the Dashboard endpoint, but is NEVER updated anywhere in the codebase. DashboardPage.tsx used it for free tier (`quota.freePostsUsed`), always showing 0. Fix: use `quota.publishedCount` (from SubscriptionData, which runs a real `COUNT(*)` query on PUBLISHED posts) for all tiers — drop the free/paid split on the frontend.

- **Settings page adds `scheduled + published` for usage**: `SettingsPage.tsx` computed `totalUsed = data.quotas.scheduled + data.quotas.published`, counting posts that haven't been published yet against the billing limit. The progress bar and "X/Y posts used" text both reflected this inflated count. Fix: use `data.quotas.published` only — scheduled posts haven't consumed quota yet.

- **Media crop modal Cancel/X feels slow because it uploads**: In `CreatePostPage.tsx` and `EditPostPage.tsx`, `PhotoCropModal`/`VideoCropModal` used `onSkip={() => advanceCropQueue(pendingFile, cropQueue)}` for Cancel/X. That path uploads the original file before clearing modal state, so Cancel/X appears delayed and unintentionally keeps the media. Fix by splitting actions: `onCancel` only clears `cropQueue`, `pendingFile`, and `pendingMediaType`; `onApply` closes the modal first and then calls `advanceCropQueue(...)` asynchronously. In `VideoCropModal`, no trim/crop should call `onApply(file)`, not the cancel path. Verify with `pnpm typecheck`, `pnpm build`, and grep the deployed Create/Edit post bundles for `onCancel` or the new cancel path.

- **Edit & Retry should be New Post-equivalent and must always requeue failed posts**: When planning or implementing failed-post retry UX, inspect `CreatePostPage.tsx`, `EditPostPage.tsx`, `PhotoCropModal.tsx`, `internal/posts/handler.go`, and publisher/enqueue lifecycle. `EditPostPage.tsx` can skip PATCH when no visible fields changed, causing Save & Retry to navigate away without resetting failed rows to `SCHEDULED`; always send retry intent/full payload for failed posts. Backend PATCH must use key presence rather than non-empty values so empty captions and intentional empty media arrays are handled/validated. Preserve crop by adding normalized crop state to the crop modal and `post_media`. If the failed target may reference a disconnected/reconnected social account, resolve retry targets by stable same-provider external ID (`ig_user_id`, Facebook `page_id`, Threads user ID), update `post_targets.account_id` to the current active row only for the same external account, and fail clearly if no matching active account exists. See `references/edit-retry-new-post-parity-and-retry-bug.md` for the plan/RCA, `references/edit-retry-save-requeue-implementation.md` for the compact implemented fix, and `references/retry-target-reconnect-resolution.md` for disconnected/reconnected account target migration.

- **Platform-aware New Post image crop planning**: When planning or implementing image crop rules for New Post, inspect `CreatePostPage.tsx`, `PhotoCropModal.tsx`, and `internal/posts/handler.go` first.

- **Platform-aware New Post image crop planning**: When planning or implementing image crop rules for New Post, inspect `CreatePostPage.tsx`, `PhotoCropModal.tsx`, and `internal/posts/handler.go` first. Centralize platform/post-type ratio rules in a small frontend requirements module, keep New Post crops ratio-locked (no `free` preset unless explicitly approved), add `9:16` for stories, treat Instagram rules as the strictest cross-posting constraint, and preserve cropper mobile/dark-mode fixes. Do not show crop-ratio lists on the main New Post form; ratio selection belongs inside the crop modal after media selection, with a large editor-style modal, right-side ratio panel, bottom thumbnail strip, and `+` add-more tile that appends to the crop queue. Queued photos must be shown as selectable thumbnails inside the same `PhotoCropModal`; clicking one should swap it into the current crop slot and keep the current file in the queue, not open another crop modal or force sequential one-by-one cropping. See `references/platform-aware-image-crop-planning.md` and `references/new-post-crop-modal-ux.md`.

- **Mobile crop panning scrolls the page / feels laggy**:

- **Post-Now navigates to SCHEDULED tab, but cron enqueues within 60s**: `CreatePostPage.tsx` navigated to `/app/posts?status=SCHEDULED` after creating a "Post Now" post (publishAt = now + 35s). The background cron runs every 60s and enqueues all SCHEDULED posts where `publish_at <= now()`, transitioning them to PUBLISHING. If the user reaches the posts page after the cron tick, the post is no longer SCHEDULED and vanishes from the filtered view. Fix: navigate to `/app/posts` (ALL tab) after creation, so the post is visible regardless of status transition.

- **Reels crop/trim stuck at `Processing… N%` is frontend FFmpeg, not backend publishing**: `VideoCropModal.tsx` runs `@ffmpeg/ffmpeg` in the browser before calling `/api/posts/media`; backend upload only happens after this finishes. Cropping (`-vf crop=...`) forces browser/WASM re-encode and can stall on normal reel-length videos, screen recordings, VFR files, or high-bitrate sources. See `references/browser-video-crop-processing.md` for the triage and fix directions.

- **Modern direct-manipulation video crop editor**: When implementing an approved modern `VideoCropModal.tsx` redesign, keep all interactive framing CSS/native-video only and run FFmpeg only for Apply/Download. Use one normalized crop state for both the clean clipped Result Preview and even-pixel FFmpeg geometry; support fit, pan, pinch/wheel/slider zoom, trim-bounded playback, and surfaced processing errors. Before deploy, compare against the approved visual artifact: Preview must actually clip to the output frame, and secondary actions such as Download must not disappear during simplification. See `references/modern-video-crop-experience.md`.

- **WhatsApp-style video trim modal UI**: When redesigning `VideoCropModal.tsx`, keep the FFmpeg trim/crop pipeline intact and change the editor shell around it: timeline above preview, duration/filesize metadata beside the timeline, live selected range + trim duration, no manual ratio selector, no blue progress bar, larger centered preview, and Download reusing the same processing function as Apply. Pass crop ratio from post context instead of letting users pick it manually (current safe default: `STORY` → `9:16`, other video posts → `free`). The timeline must be one visual filmstrip with exactly two trim handles and one playhead—not three visible native range rails. If crop gestures and playback controls share a surface, exclude interactive descendants before pointer capture so Play/Pause remains clickable. Do not call the design complete from tests/build markers alone: compare the rendered modal against the approved artifact in light/dark and mobile. See `references/whatsapp-style-video-trim-modal.md` and `references/video-crop-single-timeline-playback-controls.md`.

- **Video/carousel upload looks stuck with only `Uploading…`**: Browser `fetch()` does not expose upload progress. For `/api/posts/media`, use an XHR multipart helper with `xhr.upload.onprogress` and surface `Uploading item/total · N%` plus a progress bar in Create/Edit post flows. Keep this distinct from VideoCropModal's local `Processing… N%`. See `references/media-upload-progress.md` for the implementation pattern.

- **Reel upload fails after crop or after normal upload around 64–100 MB**: The UI promises 100 MB videos, so every upload boundary must allow that: Go `ParseMultipartForm` should be above 100 MB (128 MiB), nginx should set `client_max_body_size 128m`, and frontend upload errors should use `ApiError.code` because backend errors are shaped as `{error, code, message}`. See `references/reel-upload-size-limits.md` for the fix/verification checklist.

- **Reel uploaded/published but preview is blank**: First prove whether the backend captured media before changing upload code. Check `posts.media_thumbnail`, latest `media` rows, local/public `curl -I` for the MP4 (`Content-Type: video/mp4`), and publisher logs/`post_targets`. If media exists and publishing succeeds, inspect the API shape consumed by React: `FetchPosts` previously returned every `media[]` item as `mediaType: "IMAGE"`, causing components to render MP4 URLs with `<img>`. Fix the API boundary to emit `mediaType: "VIDEO"` for `REEL`/`VIDEO`, and render previews/lightboxes with `<video preload="metadata" playsInline controls>` where appropriate. See `references/reel-video-preview-shape-drift.md` for the compact triage recipe.

- **Instagram Reel uploaded but publishing fails with `Instagram media container not ready after 20s`**: This is a Meta container-processing timeout, not an upload/crop failure and not automatically a scope issue. Verify the MP4 exists, OAuth includes `instagram_business_content_publish`, publisher sends `media_type=REELS` + `video_url`, and logs show container timeout rather than OAuth 403. Increase Reel/video container polling to a product-safe window (2–5 minutes) and surface final container status/body. See `references/instagram-reel-container-timeout.md` for the triage checklist.

- **Instagram carousel publishes only the first photo/media item**: Do not use `posts.media_thumbnail` as the carousel media source. Persist every create/edit media item with URL, type, and position (for example `post_media`), pass the real media `url` from frontend payloads, then create IG child containers with `is_carousel_item=true` and a parent `media_type=CAROUSEL` container with `children`. Mixed media needs image children via `image_url` and video children via `media_type=VIDEO` + `video_url`. See `references/instagram-carousel-multi-media-publishing.md` for the compact fix/verification recipe.

- **Carousel preview still looks like one media after a UI fix**: Before changing upload/persistence, verify `post_media` and `/api/posts` return multiple media items. If they do, the issue is frontend presentation/cache. On mobile, small square thumbnails can still read as a single preview; use an obvious horizontal slide strip with up to 3 items, position badges (`1/N`), and `+N` overflow. Verify the deployed production chunk contains the new UI marker/class and ask for hard refresh only after production is proven current. See `references/carousel-preview-debugging.md`.

- **Carousel preview UX should make every uploaded media item reachable**: If users say carousel previews only show one upload or hidden slides cannot be opened, inspect `apps/frontend/src/components/PostCard.tsx` and `apps/frontend/src/components/PostDetailModal.tsx`. The compact card can show up to 3 items with a `+N` overlay, but the detail modal/lightbox must let users reach every `post.media` item (horizontal scroll strip or previous/next controls), preserve image/video rendering (`mediaType === "VIDEO"` or REEL/VIDEO post types use `<video>`), and display position badges (`N/total`). Keep this as a UI-only change when `post.media` already contains all items; don't chase backend persistence unless the API only returns one item.

- **Mixed image+video carousel can fail with Instagram container `status=ERROR` even when media persistence is correct**: First confirm `post_media` has all items and public URLs return valid image/video content with byte ranges. If storage is correct, don't chase the old `media_thumbnail` bug; improve `waitForInstagramContainer` to surface the full Graph status/body and verify mixed-carousel child/parent form generation. See `references/instagram-mixed-carousel-container-error.md` for triage commands and fix direction.

- **Mixed image+video carousel can fail with `Instagram media container not ready after 20s` on the parent carousel**: Even if each VIDEO child waits with a longer timeout, the parent `media_type=CAROUSEL` container can also need video-length processing time when any child is a video. Track `hasVideo` while building carousel children, create the parent, then wait up to ~3 minutes for the parent before returning it. The outer publish wait can remain unchanged because a finished parent returns immediately.

- **Facebook photo/reel publishing rules**: The create flow should not expose a Carousel post type. `PHOTO` supports one or more photos only; filter out videos and publish all ordered photo `post_media` items via `/photos`. `REEL` supports exactly one uploaded video in the UI. Backend `VIDEO`/`REEL` publishing caps ordered video items at two via `/videos` for safety, but the UI should still allow only one reel video. Do not show copy that requires a specific video format such as MP4.

- **Do not remove Instagram carousel while hiding Facebook carousel**: Carousel removal is Facebook-only. In `CreatePostPage.tsx`, keep `CAROUSEL_ALBUM` available for Instagram-only posts, with mixed photo/video uploads and up to 10 media items. Hide/reset carousel when Facebook is selected so Facebook keeps normal photo/video/text/link behavior, but do not remove the `CAROUSEL_ALBUM` type, upload purpose (`CAROUSEL_ITEM`), mixed-media accept list, multiple upload support, or PostHog carousel mapping from the Instagram create flow.

- **Facebook photo/video/reel/carousel publishing must use `post_media`, not only `posts.media_thumbnail`**: `media_thumbnail` is a single preview/fallback, so Facebook dispatch that reads only that column will drop items and can send reels as text/default posts. Reuse the ordered `post_media` list for Facebook too; handle `VIDEO` and `REEL` via `/videos`, `PHOTO`/`IMAGE` via `/photos`, and legacy `CAROUSEL_ALBUM` as photos-only. See `references/facebook-carousel-media-publishing.md` for the compact fix and regression-test shape.

- **Facebook multi-photo posts must use unpublished photos + one feed post**: Looping `POST /{page-id}/photos` with `published=true` creates separate Page posts. For 2+ photos, upload each with `published=false`, collect photo IDs, then create one `/feed` post with `attached_media[n]={"media_fbid":"..."}`. Keep the single-photo path unchanged. See `references/facebook-multi-photo-feed-publishing.md`.

- **Facebook Page analytics should reuse shared post metric columns**: When adding Facebook analytics/performance, do not build a parallel frontend path. Refresh Facebook Page metrics from `post_targets.platform_post_id` + the Page token and update `posts.likes/comments/reach/impressions/shares`; keep `saves=0` because Facebook has no Instagram-style saved count. Wire Facebook refresh anywhere Instagram refresh is called, and consider the refresh successful if either provider succeeds. See `references/facebook-page-analytics-refresh.md`.

- **Facebook Page Story publishing uses photo/video story endpoints, not feed fallback**: For `platform=facebook` + `type=STORY`, use ordered `post_media`, require exactly one public image/video URL, publish image Stories by uploading an unpublished photo then creating `/photo_stories`, and publish video Stories via `/video_stories`. Keep Instagram Story behavior unchanged (`media_type=STORIES`). See `references/facebook-page-story-publishing.md`.

- **Dual migration functions — `main.go` calls `models.Migrate()`, not `app.migrate()`**: There are TWO migration functions in the codebase: `db.go`'s `(a *app) migrate()` (used in tests) and `internal/models/models.go`'s `Migrate()` (used in `main.go` at startup). When adding a new column, BOTH functions need the `ALTER TABLE` statement. If you only update `db.go`, the column never reaches production. This caused a silent bug where `FetchPosts` returned empty results for all users because `COALESCE(p.shares,0)` failed against a missing `shares` column. **Checklist before deploying a schema change:** (1) add the ALTER TABLE to `models.Migrate()`, (2) add it to `(a *app) migrate()` in `db.go`, (3) if the live DB was created before the migration, apply it manually with `sudo sqlite3 /opt/socialzen/data/socialzen.db "ALTER TABLE …"` while the service is stopped.

- **`FetchPosts` silently swallows SQL errors**: The function does `rows, err := h.App.DB.Query(q, args...); if err != nil { return []map[string]any{} }`. Any SQL error (missing column, syntax, constraint violation) produces an empty array with no log output. When debugging "posts list is empty but DB has posts," always run the raw query manually against the live DB first: `sudo sqlite3 /opt/socialzen/data/socialzen.db "SELECT … FROM posts p LEFT JOIN instagram_accounts a ON a.id=p.instagram_account_id WHERE p.user_id='<user_id>' ORDER BY p.publish_at DESC LIMIT 5"`. If the raw SQL fails but `SELECT * FROM posts WHERE user_id='…'` succeeds, the error is in the query construction or a column reference.

- **`modernc.org/sqlite` connection deadlock with `SetMaxOpenConns > 1`**: The pure-Go SQLite driver (modernc.org/sqlite v1.34.5) deadlocks when multiple connections contend for the same database. ALL DB operations hang indefinitely while the health endpoint (no DB access) still responds. `PRAGMA busy_timeout` is ineffective — the deadlock is at the Go driver level, not the SQLite level. Fix: `db.SetMaxOpenConns(1)` + `db.SetMaxIdleConns(1)`. WAL mode still allows concurrent reads alongside writes within a single connection. If DB throughput becomes a bottleneck, switch to `mattn/go-sqlite3` (CGo) which handles connection pooling correctly. The symptom is POST endpoints (sign-in, sign-up) timing out after 15s frontend timeout while GET-only endpoints without DB access still work. Auth handlers should use `context.WithTimeout` and `QueryRowContext`/`ExecContext` for login/signup/session creation so DB stalls fail quickly instead of leaving mobile preview stuck on the generic timeout message.

- **Single SQLite connection means no nested DB queries while `Rows` is open**: Because production intentionally uses `SetMaxOpenConns(1)`, any handler that iterates `rows.Next()` and calls another DB query inside the loop will self-block waiting for the only connection. This makes logged-in pages like Dashboard/Posts/Analytics/comments hang while `/health` stays fast. Fix by reading rows into a small in-memory slice, calling `rows.Close()`, then running enrichment queries (`fetchPostMedia`, `fetchTargets`, Facebook page names, `isLiked`, `fetchReplies`, etc.). Apply the same rule to helper functions: don't `defer rows.Close()` if the function performs another query before returning or building DTOs; close explicitly before the next query. Specific observed pitfall: `fetchPostMedia()` with no `post_media` rows returned thumbnail fallback before closing its cursor, so `/api/posts` hung and published posts looked like they disappeared after restart. Comment-list pitfall: `listComments()` and `fetchReplies()` can deadlock if they keep `Rows` open while checking likes or loading replies. Regression guard: configure test DBs with `SetMaxOpenConns(1)` so nested-cursor deadlocks fail in tests instead of only production. See `references/posts-list-deadlock-empty-media.md` and `references/comment-list-sqlite-deadlock.md`.

- **Profile avatar upload should crop before upload by reusing the existing photo cropper**: Settings profile upload lives in `apps/frontend/src/pages/settings/SettingsPage.tsx`; the reusable cropper is `apps/frontend/src/components/PhotoCropModal.tsx`. For avatar crop requests, do not add a new crop dependency. Add small reusable props to `PhotoCropModal` such as `title` and `defaultPreset`, then store the selected file in `pendingAvatar`, open the modal with `title="Crop profile photo"` and `defaultPreset="1:1"`, upload only the cropped file on Apply, and make Cancel/X clear `pendingAvatar` without uploading. Keep the existing JPEG/PNG/WebP + max-size validation before opening the cropper and disable/show `Uploading…` during upload.

- **Avatar not shown in Topbar/Sidebar + stale after upload**: The Topbar (`components/Topbar.tsx`) had no avatar display at all — only a title, subtitle, and Schedule button. The Sidebar user chip only showed initials, never the uploaded avatar. After fixing both to show `session?.user.avatarUrl`, the avatar still appeared stale for up to 5 minutes because `authClient.useSession()` uses a 5-minute TTL module-level cache. Fix: (1) add avatar `<img>` to Topbar (right side, next to Schedule) and Sidebar user chip, with initials gradient as fallback; (2) in SettingsPage, call `authClient.refreshSession()` after `uploadAvatar()` and `deleteAvatar()` to bust the cache immediately.

- **Profile avatar crop should reuse the existing photo cropper**: For crop-before-upload in Settings → Profile, reuse `PhotoCropModal` from the post media flow instead of adding a crop dependency. Keep a pending avatar file state, validate JPEG/PNG/WebP + max size before opening the modal, default to square crop, and make Cancel/X clear state without uploading. Apply uploads only the cropped file through `uploadAvatar()` and still calls `authClient.refreshSession()` for immediate Topbar/Sidebar refresh. See `references/profile-avatar-crop-reuse.md`.

- **PhotoCropModal should not show decorative emoji/editor toolbar text**: The cropper header once rendered hardcoded decorative icons (`✂ ✨ ✎ T □ ▦ ☺ ☁ ▭`) next to the title. If the user reports a weird cropped photo emoji/icon row, remove that header toolbar entirely; keep only the title and actual crop controls. Verify by grepping the built `PhotoCropModal-*.js` for the distinctive emoji characters from `apps/frontend/dist`, not the repo root.

- **Google Sign-In should use GIS ID token → existing session cookie**: For SocialZen app-login, use Google Identity Services on the frontend only to obtain an ID token, verify it server-side with Google JWKS, then issue the existing `brand_session` cookie. Keep provider identities in `user_identities`, link existing users only by verified Google email, reject password login for Google-only users with empty password hashes, remove Instagram from app-login screens, and keep both migration paths (`db.go` and `internal/models/models.go`) in sync. See `references/google-sign-in-gis-implementation.md`.

- **Google identity conflict hardening must reject unsafe merges**: Treat Google `sub` as the stable identity and verified email as a linking hint only. If a new `sub` reuses an email already tied to another Google identity, or an existing `sub` returns an email owned by another canonical user, return `409 ACCOUNT_LINK_CONFLICT` and preserve the backend code through the frontend for actionable Login/Signup copy. See `references/google-identity-conflict-hardening.md`.

- **Auth security separation should extend `user_identities`, not provider columns on `users`**: For SocialZen app-login changes, keep Email+Password and OAuth provider methods as separate auth methods for one canonical `users.id`. Signup creates email/password accounts; login never creates unknown emails; Google Sign-In links by stable `sub` first and verified email only as a linking hint; Google-only users can add a SocialZen password later. Replace the current SHA-256 password hash path with bcrypt/Argon2id while transparently upgrading legacy hashes after successful login, add Settings → Security for Change/Add Password, and add rate limiting/conflict handling. If the user asks to execute with the least token/smallest safe diff, start with the password foundation and `user_tokens` migrations before larger email/UX stages; see `references/auth-password-hardening-foundation.md`, `references/auth-token-foundation.md`, and `references/auth-security-separation-and-provider-identities.md`.

- **Settings → Security password add/change implementation**: Keep this as a small authenticated Settings slice: `GET /api/auth/security` returns whether the canonical user has a password, `POST /api/auth/password` adds a password for Google-only users or requires `currentPassword` for password users, hashes with the existing helper, marks email verified, preserves the current session while deleting other sessions, and queues a password-changed email. Frontend lives in `SettingsPage.tsx` as an app-native `SecurityTab`; remember to add the settings translation key and widen `Event.SETTINGS_CHANGED` section typing. See `references/settings-password-security.md`.

- **Auth token foundation requires a real pepper, never a fallback**: For password reset, email verification, magic-link, or invite token support, require `AUTH_TOKEN_PEPPER` from the server environment and fail startup clearly when it is missing. Do not hardcode a dev value. Store only HMAC-SHA256 token hashes in `user_tokens`, consume them once, and update both production and test migration paths. See `references/auth-token-foundation.md`.

- **Auth email provider uses `RESEND_KEY`, not `RESEND_API_KEY`**: When implementing verification/reset email phases, read Resend credentials from `RESEND_KEY` only, keep empty/`test`/`none` email provider as no-send mode, issue signup verification after session creation so provider delays don't block signup, and smoke forgot-password with an unknown email to avoid sending real reset links. If deploying this phase, verify the service env linkage and use the compact targeted test/build/smoke recipe in `references/transactional-email-provider-deploy-verification.md`. See also `references/auth-email-token-provider-implementation.md`.

- **Auth token lifecycle endpoints**: After the `user_tokens` foundation exists, expose reset/verify/resend through small backend endpoints that consume tokens via `models.TokenService` instead of duplicating token checks. Keep forgot-password enumeration-safe, reject token reuse, avoid raw token URL logs, and keep Resend config/tests on `RESEND_KEY` only. See `references/auth-token-lifecycle-endpoints.md` for the compact implementation pattern.

- **Auth abuse-prevention hardening**: After core auth endpoints exist, add a small dispatch-level guard for sensitive auth rate limits and cookie-authenticated mutation Origin checks, preserve `HttpOnly`/`SameSite=Lax` cookies with `Secure` on HTTPS/forwarded HTTPS, audit auth events to SQLite, and run old-token cleanup from a server ticker. Add `auth_audit_logs` to both migration paths and strip ephemeral ports from `RemoteAddr` before using it as a rate-limit key. See `references/auth-abuse-prevention-hardening.md` for the compact test/deploy/smoke recipe.

- **Frontend auth UX gates**: For the auth frontend slice, keep the work small and user-visible: signup should show check-email when `session.user.emailVerified` is false, login should map `PASSWORD_NOT_SET` to Google/password guidance, and Create Post/social OAuth helpers should surface `EMAIL_NOT_VERIFIED` clearly. Prefer `ApiError.code` over nested body inspection for these frontend gates. See `references/frontend-auth-ux-gates.md`.

- **Forgot/reset password implementation**: For password recovery, reuse `models.TokenService` and `user_tokens`; never store raw reset tokens. Forgot password must return the same success shape for existing, missing, and Google-only emails, but only issue password-reset tokens for users with a local `password_hash != ''`. The frontend reset link route is `/auth/reset-password?token=...` and posts `{ token, password }` to `/api/auth/reset-password`. See `references/forgot-reset-password-implementation.md` for the compact implementation and verification recipe.

- **Email verification implementation gates real actions and protected app routes**: Email/password signup should store `email_verified=0`, queue verification after session creation, and verify through a frontend `/auth/verify-email?token=...` page that refreshes the session. When product policy requires verification before dashboard access, gate `/app/*` at the shared protected-route boundary and redirect to a public verification-required page with resend, refresh, and sign-out; keep backend action gates because frontend routing is not security. Google’s validated `email_verified=true` claim satisfies verification, and both new-link and existing-subject identity branches must upgrade the canonical user row after conflict checks. Forgot-password stays enumeration-safe while UI copy truthfully directs Google-only users to Google Sign-In. See `references/email-verification-flow-implementation.md` for the token/action baseline and `references/auth-dashboard-verification-gate.md` for route tests, Google-link edge cases, subpath URL configuration, and deployment verification.

- **Schedule navigation exists in multiple places**: The desktop Topbar `+ Schedule` already routes to `/app/calendar`, but the Dashboard quick-action `+ Schedule` in `pages/dashboard/DashboardPage.tsx` can drift separately. When changing Schedule/create navigation, grep for both `+ Schedule` and `/app/posts/new` across the frontend and keep intended entry points consistent. Verify the built dashboard chunk contains `/app/calendar` after deploy.

- **Mobile app shell/navigation changes need AppLayout + Topbar + Settings coordination**: The global shell lives in `AppLayout.tsx`, desktop nav lives in `Sidebar.tsx`, mobile drawer entry is the `Topbar` hamburger via `SidebarContext.openSidebar()`, and Settings has its own internal mobile/desktop settings navigation. When replacing mobile primary navigation, use the existing `md` breakpoint, keep desktop sidebar untouched, remove/gate the hamburger so it is not a dead duplicate, add safe-area-aware bottom spacing to AppLayout's internal scroll container, and hide global mobile nav on `/app/settings` so Settings keeps its own layout. See `references/mobile-navigation-shell.md`.

- **Mobile Settings must be a route hub, not tabs with content underneath**: On mobile, `/app/settings` should render only the settings section list, and each section should live at `/app/settings/:section` with a back header and reused existing section component. Keep desktop/tablet as the existing sidebar/tabbed layout. The mobile detail header should include an obvious, separate tappable back button with a left-arrow icon (for example `ArrowLeft` from `lucide-react`) next to the section title; do not rely on a combined text label like `← Profile`, which can be missed on phone screenshots. Redirect legacy `?tab=` deep links to the section route and update banners/links accordingly. In `App.tsx`, keep explicit `settings` and `settings/:section` routes; do not replace them with only `settings/*` or leave duplicate/wildcard route confusion that can mask section behavior. After build/deploy, grep the deployed SettingsPage chunk for `Back to Settings` or another distinctive marker and verify the chunk returns `application/javascript`. See `references/mobile-settings-navigation-hub.md`.

- **Mobile Profile logout belongs directly below Timezone**: In `SettingsPage.tsx`, place the Profile logout action immediately after the Timezone selector and gate it with `md:hidden` so desktop Settings remains unchanged. Reuse `authClient.signOut()` and navigate to `/login` with `{ replace: true }`; do not introduce another logout/session helper. Use a full-width accessible destructive-outline button with a `LogOut` icon, disable it while signing out, and surface failures through the Profile tab's existing feedback state. Verify with `pnpm typecheck`, `pnpm build`, grep the built `SettingsPage-*.js` for the logout marker, deploy the frontend, and confirm the public chunk returns `application/javascript`.

- **Settings quick menu redesign**: When replacing Settings navigation with a Tokopedia-like horizontal quick menu, keep existing section internals untouched, use data-driven Lucide icon buttons in a reusable `SettingsQuickMenu`, hide the mobile horizontal scrollbar with Tailwind arbitrary selectors, wire accessible active state + smooth `scrollIntoView`, and verify the deployed SettingsPage chunk content type. See `references/settings-quick-menu-redesign.md`.

- **Language switch belongs in Settings → Accessibility, with Indonesian default**: For SocialZen i18n/language requests, create or update a Settings `accessibility` section and place the Indonesian/English switch there. Default fresh users to Indonesian (`id-ID`), persist the selected language client-side unless cross-device sync is requested, and update `<html lang>` for accessibility. Prefer a tiny in-app `t(key)`/language helper before adding an i18n dependency on the first pass. Publish the review plan before implementation. For the implementation pattern, storage key, tests, deployment, and bundle-marker verification, see `references/language-accessibility-i18n-implementation.md`; for plan-first expectations, see `references/language-accessibility-i18n-planning.md`.

- **Accessibility language selector polish**: If the Settings → Accessibility language picker looks like a native/basic dropdown, keep the existing language helper and `components/ui/select`, but present it as a modern settings card: token-based `var(--card)/(--bg)/(--line)` backgrounds, a clear active-language line, larger rounded trigger (`h-12`, full-width on mobile, fixed width on desktop), improved card padding/radius, and light/dark-safe icon treatment. Do not add a new select library for this.

- **Photo crop add-more tile contrast**: In `PhotoCropModal.tsx`, the bottom thumbnail strip's `onAddMore` button must read as an obvious add-photo tile, not a faint translucent `+`. Match thumbnail dimensions/radius, use a token-based high-contrast class in `globals.css`, and include hover, active, `focus-visible`, `aria-label`, and `title`. Keep the existing cropper logic unchanged when this is only a UI contrast issue.

- **Photo crop multi-image state needs File identity, a load-boundary gate, stable order, and atomic Apply**: If switching uploaded crop thumbnails makes a crop shrink, mutate another image, jump back, or reorder the carousel, inspect `PhotoCropModal.tsx` persistence and the parent state model before changing crop math. Key memory with `WeakMap<File, CropState>`—never `name:size:lastModified`—and persist only after the exact current file has loaded. Keep one stable ordered `File[]` for upload/carousel order and track editor selection separately; thumbnail clicks must never swap files or promote the selected image to position 1. Parent setters must be direct, not nested in another state updater. For batch Apply, materialize and validate every image first, preserve original order, and upload none if any ratio is invalid; keep the modal open and select the first invalid image. Validate generated dimensions with proportional ratio tolerance (for example 1%), not a fixed one-pixel tolerance: display-space rounding can become several pixels after scaling to source resolution and falsely reject a correctly auto-cropped photo. Keep single-image callers strongly typed rather than widening callbacks to `any`. See `references/photo-crop-independent-file-state.md`, `references/photo-crop-file-switch-race.md`, and `references/photo-crop-stable-order-atomic-batch.md`.

- **Calendar crowded-day review UX**: If users say month calendar days with many posts are hard to inspect, keep the monthly calendar fetch and add a deliberate date/day-list dialog instead of a backend endpoint. Preserve drag/drop by making only the date number or `View all (N)` affordance clickable, not the whole droppable day cell. If the user says clicking a post in calendar should not open detail, make the small in-grid post card open the day-list dialog/card for that date; the post detail can remain reachable from the list item. Group and sort both grid-day posts and dialog posts through one shared helper (`postsByLocalDay`/`postsForLocalDay`) so the visible list is in publish-time order. The grid and dialog must use the same selected-day key; if the grid keys cells with `format(day, "yyyy-MM-dd")`, do not re-zone that selected cell date inside `postsForLocalDay`, or browser/profile timezone drift can make the popup empty while the grid shows posts. Minimal fix: `const dayKey = format(day, "yyyy-MM-dd")` in `postsForLocalDay`, while `postsByLocalDay` still groups post publish times via `format(toZonedTime(post.publishAt, userTimezone), "yyyy-MM-dd")`. Add a regression in `apps/frontend/src/lib/calendar-day.test.ts` using a browser-selected cell date such as `new Date(2026, 6, 24)` plus `America/Los_Angeles` and a UTC post that lands on that local day. See `references/calendar-day-post-list.md` and `references/calendar-selected-day-timezone-drift.md`.
