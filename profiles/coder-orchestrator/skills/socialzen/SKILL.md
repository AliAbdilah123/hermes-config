---
name: socialzen
description: Maintain, deploy, and debug the SocialZen social-media scheduling app (Go + React, Instagram/Facebook/Threads publishing).
---

# SocialZen Project

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

- **Facebook-only posts misclassified as cross-platform by post-target backfill**: Keep every post-target backfill guarded with `WHERE NOT EXISTS (SELECT 1 FROM post_targets pt WHERE pt.post_id=p.id)`. SocialZen has legacy/test migration paths in `apps/backend-go/db.go` in addition to production `internal/models.Migrate()`; if those paths backfill Instagram targets for all posts, a Facebook-only post can later receive an extra Instagram target and be treated as cross-platform. Regression check: create `platforms:["facebook"]` + `facebookPageId`, then assert zero Instagram targets and one Facebook target in `post_targets`.

- **User may see old frontend after deploy**: The JS bundle filename changes (hash), but browser may cache the old HTML. User needs a hard refresh (Ctrl+Shift+R).
- **Cloudflare SPA fallback caching**: If frontend is deployed to the WRONG directory (or before rsync finishes), nginx's `try_files` falls through to `index.html` for JS/CSS requests. Cloudflare caches that HTML as the JS file (`content-type: text/html`, `cf-cache-status: HIT`), breaking the entire app until the Cloudflare cache expires (4-hour `max-age`). Verify with: `curl -sI "https://socialzen.ahsanworks.com/projects/socialzen/assets/<some-file>.js" | grep content-type`. If it returns `text/html` instead of `application/javascript`, deploy to the correct path and wait for cache expiry or purge Cloudflare.
- **Facebook reconnect needed after scope change**: If Facebook scopes change, existing connections don't get the new scope. User must reconnect in Settings → Accounts.
- **Instagram account disconnect**: If a post's `instagram_account_id` points to a deleted account, publishing fails with "Instagram account not connected." The user needs to reconnect Instagram.
- **Threads OAuth saves to wrong table**: Without explicit Threads handling, Threads accounts were saved to `instagram_accounts` instead of `threads_accounts`. Fixed in `instagram_oauth.go` — Threads callback now inserts into `threads_accounts` with correct schema and performs long-lived token exchange via `th_exchange_token`.
- **Settings active-tab theming**: The Settings page has a secondary left nav (`apps/frontend/src/pages/settings/SettingsPage.tsx`) beside the main sidebar. Its active state should match the sidebar's active purple pill. Use Tailwind tokens `bg-primary text-primary-foreground`; avoid `bg-[var(--ink)] text-white`, which renders as a black/white selected tab and looks inconsistent in dark mode.

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
- **Analytics includes non-published posts**: `analyticsOverview` passed ALL posts (SCHEDULED, FAILED, DRAFT) to `analyticsSummary()`, dragging averages to zero. Fix: filter to `status == "PUBLISHED"` before computing aggregates. Also, `analyticsRefresh` should call `comments.RefreshPostInsights()` (reach, impressions, saves) in addition to `RefreshPostMetrics()` (likes, comments).
- **Posts page filters can hide newly-created posts if backend ignores query params**: The Posts page sends `status`, `account_id`, `search`, `limit`, and `offset` to `/api/posts`; `ListPosts` must actually pass those into `FetchPosts`. If the user says a just-published/scheduled/failed post is absent under every filter, inspect both the POST creation result and the list query. `FetchPosts` should filter in SQL and use `LEFT JOIN instagram_accounts`, not `JOIN`, because Facebook-only or stale-Instagram-account posts can otherwise exist in `posts`/`post_targets` but vanish from every Posts page tab.
- **Dashboard placeholder card contrast**: On the Dashboard fallback cards, don't use low-opacity theme text when the card background is extreme. The lime/yellow follower placeholder needs explicit dark text (black/near-black), and the dark top-post placeholder needs explicit white text so it stays readable in both light and dark modes.
- **Delete post doesn't cascade to platforms**: The DELETE handler only removed local DB rows. Must first look up `platform_post_id` from `post_targets` for PUBLISHED targets and call the platform's DELETE API: Instagram `DELETE /{ig-user-id}/media?access_token=...`, Facebook `DELETE /{page-id}_{post-id}?access_token=...`. Then clean up `post_targets`, `instagram_comments`, and `posts`.

- **Dark mode: preset buttons with `var(--ink)` background + `#fff` text = invisible in dark mode**: In PhotoCropModal and VideoCropModal, the selected ratio-preset button uses `background: "var(--ink)"` with `color: "#fff"`. In dark mode, `--ink` = `#f7f2ff` (near-white), so white text is invisible. Fix: selected text should use `color: "var(--bg)"` (dark bg in dark mode), non-selected background should use `var(--card)` instead of hardcoded `#fff` so it picks up the dark-mode card color.

- **REEL/VIDEO not supported by Instagram publisher**: `publishInstagramImage()` in `publisher.go` had a hard gate: `if post.typ != "PHOTO" && post.typ != "IMAGE" { return error }`. REEL and VIDEO types were rejected with "Instagram publishing supports images only." Fix: modify `createInstagramMediaContainer()` to accept post type — for REEL/VIDEO, send `media_type=REELS` and `video_url` to the Instagram `/media` endpoint. For PHOTO/IMAGE/CAROUSEL_ALBUM, send `image_url` as before.

- **Billing: `freePostsUsed` column never incremented**: The `free_posts_used` column on the `users` table exists and is read by the Dashboard endpoint, but is NEVER updated anywhere in the codebase. DashboardPage.tsx used it for free tier (`quota.freePostsUsed`), always showing 0. Fix: use `quota.publishedCount` (from SubscriptionData, which runs a real `COUNT(*)` query on PUBLISHED posts) for all tiers — drop the free/paid split on the frontend.

- **Settings page adds `scheduled + published` for usage**: `SettingsPage.tsx` computed `totalUsed = data.quotas.scheduled + data.quotas.published`, counting posts that haven't been published yet against the billing limit. The progress bar and "X/Y posts used" text both reflected this inflated count. Fix: use `data.quotas.published` only — scheduled posts haven't consumed quota yet.

- **Media crop modal Cancel/X feels slow because it uploads**: In `CreatePostPage.tsx` and `EditPostPage.tsx`, `PhotoCropModal`/`VideoCropModal` used `onSkip={() => advanceCropQueue(pendingFile, cropQueue)}` for Cancel/X. That path uploads the original file before clearing modal state, so Cancel/X appears delayed and unintentionally keeps the media. Fix by splitting actions: `onCancel` only clears `cropQueue`, `pendingFile`, and `pendingMediaType`; `onApply` closes the modal first and then calls `advanceCropQueue(...)` asynchronously. In `VideoCropModal`, no trim/crop should call `onApply(file)`, not the cancel path. Verify with `pnpm typecheck`, `pnpm build`, and grep the deployed Create/Edit post bundles for `onCancel` or the new cancel path.

- **Post-Now navigates to SCHEDULED tab, but cron enqueues within 60s**: `CreatePostPage.tsx` navigated to `/app/posts?status=SCHEDULED` after creating a "Post Now" post (publishAt = now + 35s). The background cron runs every 60s and enqueues all SCHEDULED posts where `publish_at <= now()`, transitioning them to PUBLISHING. If the user reaches the posts page after the cron tick, the post is no longer SCHEDULED and vanishes from the filtered view. Fix: navigate to `/app/posts` (ALL tab) after creation, so the post is visible regardless of status transition.

- **Reels crop/trim stuck at `Processing… N%` is frontend FFmpeg, not backend publishing**: `VideoCropModal.tsx` runs `@ffmpeg/ffmpeg` in the browser before calling `/api/posts/media`; backend upload only happens after this finishes. Cropping (`-vf crop=...`) forces browser/WASM re-encode and can stall on normal reel-length videos, screen recordings, VFR files, or high-bitrate sources. See `references/browser-video-crop-processing.md` for the triage and fix directions.

- **Video/carousel upload looks stuck with only `Uploading…`**: Browser `fetch()` does not expose upload progress. For `/api/posts/media`, use an XHR multipart helper with `xhr.upload.onprogress` and surface `Uploading item/total · N%` plus a progress bar in Create/Edit post flows. Keep this distinct from VideoCropModal's local `Processing… N%`. See `references/media-upload-progress.md` for the implementation pattern.

- **Reel upload fails after crop or after normal upload around 64–100 MB**: The UI promises 100 MB videos, so every upload boundary must allow that: Go `ParseMultipartForm` should be above 100 MB (128 MiB), nginx should set `client_max_body_size 128m`, and frontend upload errors should use `ApiError.code` because backend errors are shaped as `{error, code, message}`. See `references/reel-upload-size-limits.md` for the fix/verification checklist.

- **Reel uploaded/published but preview is blank**: First prove whether the backend captured media before changing upload code. Check `posts.media_thumbnail`, latest `media` rows, local/public `curl -I` for the MP4 (`Content-Type: video/mp4`), and publisher logs/`post_targets`. If media exists and publishing succeeds, inspect the API shape consumed by React: `FetchPosts` previously returned every `media[]` item as `mediaType: "IMAGE"`, causing components to render MP4 URLs with `<img>`. Fix the API boundary to emit `mediaType: "VIDEO"` for `REEL`/`VIDEO`, and render previews/lightboxes with `<video preload="metadata" playsInline controls>` where appropriate. See `references/reel-video-preview-shape-drift.md` for the compact triage recipe.

- **Instagram Reel uploaded but publishing fails with `Instagram media container not ready after 20s`**: This is a Meta container-processing timeout, not an upload/crop failure and not automatically a scope issue. Verify the MP4 exists, OAuth includes `instagram_business_content_publish`, publisher sends `media_type=REELS` + `video_url`, and logs show container timeout rather than OAuth 403. Increase Reel/video container polling to a product-safe window (2–5 minutes) and surface final container status/body. See `references/instagram-reel-container-timeout.md` for the triage checklist.

- **Instagram carousel publishes only the first photo/media item**: Do not use `posts.media_thumbnail` as the carousel media source. Persist every create/edit media item with URL, type, and position (for example `post_media`), pass the real media `url` from frontend payloads, then create IG child containers with `is_carousel_item=true` and a parent `media_type=CAROUSEL` container with `children`. Mixed media needs image children via `image_url` and video children via `media_type=VIDEO` + `video_url`. See `references/instagram-carousel-multi-media-publishing.md` for the compact fix/verification recipe.

- **Dual migration functions — `main.go` calls `models.Migrate()`, not `app.migrate()`**: There are TWO migration functions in the codebase: `db.go`'s `(a *app) migrate()` (used in tests) and `internal/models/models.go`'s `Migrate()` (used in `main.go` at startup). When adding a new column, BOTH functions need the `ALTER TABLE` statement. If you only update `db.go`, the column never reaches production. This caused a silent bug where `FetchPosts` returned empty results for all users because `COALESCE(p.shares,0)` failed against a missing `shares` column. **Checklist before deploying a schema change:** (1) add the ALTER TABLE to `models.Migrate()`, (2) add it to `(a *app) migrate()` in `db.go`, (3) if the live DB was created before the migration, apply it manually with `sudo sqlite3 /opt/socialzen/data/socialzen.db "ALTER TABLE …"` while the service is stopped.

- **`FetchPosts` silently swallows SQL errors**: The function does `rows, err := h.App.DB.Query(q, args...); if err != nil { return []map[string]any{} }`. Any SQL error (missing column, syntax, constraint violation) produces an empty array with no log output. When debugging "posts list is empty but DB has posts," always run the raw query manually against the live DB first: `sudo sqlite3 /opt/socialzen/data/socialzen.db "SELECT … FROM posts p LEFT JOIN instagram_accounts a ON a.id=p.instagram_account_id WHERE p.user_id='<user_id>' ORDER BY p.publish_at DESC LIMIT 5"`. If the raw SQL fails but `SELECT * FROM posts WHERE user_id='…'` succeeds, the error is in the query construction or a column reference.

- **`modernc.org/sqlite` connection deadlock with `SetMaxOpenConns > 1`**: The pure-Go SQLite driver (modernc.org/sqlite v1.34.5) deadlocks when multiple connections contend for the same database. ALL DB operations hang indefinitely while the health endpoint (no DB access) still responds. `PRAGMA busy_timeout` is ineffective — the deadlock is at the Go driver level, not the SQLite level. Fix: `db.SetMaxOpenConns(1)` + `db.SetMaxIdleConns(1)`. WAL mode still allows concurrent reads alongside writes within a single connection. If DB throughput becomes a bottleneck, switch to `mattn/go-sqlite3` (CGo) which handles connection pooling correctly. The symptom is POST endpoints (sign-in, sign-up) timing out after 15s frontend timeout while GET-only endpoints without DB access still work.

- **Avatar not shown in Topbar/Sidebar + stale after upload**: The Topbar (`components/Topbar.tsx`) had no avatar display at all — only a title, subtitle, and Schedule button. The Sidebar user chip only showed initials, never the uploaded avatar. After fixing both to show `session?.user.avatarUrl`, the avatar still appeared stale for up to 5 minutes because `authClient.useSession()` uses a 5-minute TTL module-level cache. Fix: (1) add avatar `<img>` to Topbar (right side, next to Schedule) and Sidebar user chip, with initials gradient as fallback; (2) in SettingsPage, call `authClient.refreshSession()` after `uploadAvatar()` and `deleteAvatar()` to bust the cache immediately.
