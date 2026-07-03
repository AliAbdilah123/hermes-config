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

Facebook Page publishing (`POST /{page-id}/feed`, `/photos`, `/videos`) requires `pages_manage_posts` + `pages_read_engagement` on the Page token. If Facebook publishing fails with a 403 mentioning `pages_manage_posts`, make sure `facebookScopes` in `instagram_oauth.go` includes `pages_manage_posts`, deploy, then reconnect Facebook in Settings → Accounts so the saved Page token gets the new scope.

Current required scopes: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `business_management`.

If Meta OAuth shows "Invalid Scopes: pages_manage_posts", the Facebook app likely needs App Review / Advanced Access or the user must be an app admin/developer/tester in Development mode. See `references/facebook-scope-errors.md` for historical error transcripts.

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
- **Comment GET blocks the response**: In `internal/comments/handler.go`, `syncInstagramComments()` was called synchronously on GET, making HTTP calls to Instagram's API (1-5s) before returning the comment list. MUST run as `go h.syncInstagramComments(...)` — the sync fetches from Instagram in the background while the local DB result is returned immediately.
- **Analytics includes non-published posts**: `analyticsOverview` passed ALL posts (SCHEDULED, FAILED, DRAFT) to `analyticsSummary()`, dragging averages to zero. Fix: filter to `status == "PUBLISHED"` before computing aggregates. Also, `analyticsRefresh` should call `comments.RefreshPostInsights()` (reach, impressions, saves) in addition to `RefreshPostMetrics()` (likes, comments).
- **Posts page filters can hide newly-created posts if backend ignores query params**: The Posts page sends `status`, `account_id`, `search`, `limit`, and `offset` to `/api/posts`; `ListPosts` must actually pass those into `FetchPosts`. If the user says a just-published/scheduled/failed post is absent under every filter, inspect both the POST creation result and the list query. `FetchPosts` should filter in SQL and use `LEFT JOIN instagram_accounts`, not `JOIN`, because Facebook-only or stale-Instagram-account posts can otherwise exist in `posts`/`post_targets` but vanish from every Posts page tab.
- **Dashboard placeholder card contrast**: On the Dashboard fallback cards, don't use low-opacity theme text when the card background is extreme. The lime/yellow follower placeholder needs explicit dark text (black/near-black), and the dark top-post placeholder needs explicit white text so it stays readable in both light and dark modes.
- **Delete post doesn't cascade to platforms**: The DELETE handler only removed local DB rows. Must first look up `platform_post_id` from `post_targets` for PUBLISHED targets and call the platform's DELETE API: Instagram `DELETE /{ig-user-id}/media?access_token=...`, Facebook `DELETE /{page-id}_{post-id}?access_token=...`. Then clean up `post_targets`, `instagram_comments`, and `posts`.

- **Dark mode: preset buttons with `var(--ink)` background + `#fff` text = invisible in dark mode**: In PhotoCropModal and VideoCropModal, the selected ratio-preset button uses `background: "var(--ink)"` with `color: "#fff"`. In dark mode, `--ink` = `#f7f2ff` (near-white), so white text is invisible. Fix: selected text should use `color: "var(--bg)"` (dark bg in dark mode), non-selected background should use `var(--card)` instead of hardcoded `#fff` so it picks up the dark-mode card color.

- **REEL/VIDEO not supported by Instagram publisher**: `publishInstagramImage()` in `publisher.go` had a hard gate: `if post.typ != "PHOTO" && post.typ != "IMAGE" { return error }`. REEL and VIDEO types were rejected with "Instagram publishing supports images only." Fix: modify `createInstagramMediaContainer()` to accept post type — for REEL/VIDEO, send `media_type=REELS` and `video_url` to the Instagram `/media` endpoint. For PHOTO/IMAGE/CAROUSEL_ALBUM, send `image_url` as before.

- **Billing: `freePostsUsed` column never incremented**: The `free_posts_used` column on the `users` table exists and is read by the Dashboard endpoint, but is NEVER updated anywhere in the codebase. DashboardPage.tsx used it for free tier (`quota.freePostsUsed`), always showing 0. Fix: use `quota.publishedCount` (from SubscriptionData, which runs a real `COUNT(*)` query on PUBLISHED posts) for all tiers — drop the free/paid split on the frontend.

- **Settings page adds `scheduled + published` for usage**: `SettingsPage.tsx` computed `totalUsed = data.quotas.scheduled + data.quotas.published`, counting posts that haven't been published yet against the billing limit. The progress bar and "X/Y posts used" text both reflected this inflated count. Fix: use `data.quotas.published` only — scheduled posts haven't consumed quota yet.

- **Post-Now navigates to SCHEDULED tab, but cron enqueues within 60s**: `CreatePostPage.tsx` navigated to `/app/posts?status=SCHEDULED` after creating a "Post Now" post (publishAt = now + 35s). The background cron runs every 60s and enqueues all SCHEDULED posts where `publish_at <= now()`, transitioning them to PUBLISHING. If the user reaches the posts page after the cron tick, the post is no longer SCHEDULED and vanishes from the filtered view. Fix: navigate to `/app/posts` (ALL tab) after creation, so the post is visible regardless of status transition.

- **Dual migration functions — `main.go` calls `models.Migrate()`, not `app.migrate()`**: There are TWO migration functions in the codebase: `db.go`'s `(a *app) migrate()` (used in tests) and `internal/models/models.go`'s `Migrate()` (used in `main.go` at startup). When adding a new column, BOTH functions need the `ALTER TABLE` statement. If you only update `db.go`, the column never reaches production. This caused a silent bug where `FetchPosts` returned empty results for all users because `COALESCE(p.shares,0)` failed against a missing `shares` column. **Checklist before deploying a schema change:** (1) add the ALTER TABLE to `models.Migrate()`, (2) add it to `(a *app) migrate()` in `db.go`, (3) if the live DB was created before the migration, apply it manually with `sudo sqlite3 /opt/socialzen/data/socialzen.db "ALTER TABLE …"` while the service is stopped.

- **`FetchPosts` silently swallows SQL errors**: The function does `rows, err := h.App.DB.Query(q, args...); if err != nil { return []map[string]any{} }`. Any SQL error (missing column, syntax, constraint violation) produces an empty array with no log output. When debugging "posts list is empty but DB has posts," always run the raw query manually against the live DB first: `sudo sqlite3 /opt/socialzen/data/socialzen.db "SELECT … FROM posts p LEFT JOIN instagram_accounts a ON a.id=p.instagram_account_id WHERE p.user_id='<user_id>' ORDER BY p.publish_at DESC LIMIT 5"`. If the raw SQL fails but `SELECT * FROM posts WHERE user_id='…'` succeeds, the error is in the query construction or a column reference.

- **Avatar not shown in Topbar/Sidebar + stale after upload**: The Topbar (`components/Topbar.tsx`) had no avatar display at all — only a title, subtitle, and Schedule button. The Sidebar user chip only showed initials, never the uploaded avatar. After fixing both to show `session?.user.avatarUrl`, the avatar still appeared stale for up to 5 minutes because `authClient.useSession()` uses a 5-minute TTL module-level cache. Fix: (1) add avatar `<img>` to Topbar (right side, next to Schedule) and Sidebar user chip, with initials gradient as fallback; (2) in SettingsPage, call `authClient.refreshSession()` after `uploadAvatar()` and `deleteAvatar()` to bust the cache immediately.
