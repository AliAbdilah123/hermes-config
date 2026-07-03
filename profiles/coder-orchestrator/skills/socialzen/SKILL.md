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

## Facebook Platform Limitation

**`pages_manage_posts` scope is NOT valid for regular Facebook apps.** Adding it to `facebookScopes` causes Meta's OAuth dialog to show "Invalid Scopes: pages_manage_posts" and blocks authentication.

Facebook Page publishing (`POST /{page-id}/feed`) requires `pages_manage_posts` + `pages_read_engagement`. This means Facebook direct publishing is unavailable unless the Facebook app is upgraded to **Business type** with Advanced Access.

Current scopes (safe for regular apps): `pages_show_list`, `pages_read_engagement`, `business_management`.

See `references/facebook-scope-errors.md` for full error transcripts.

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
- **Dark mode white-on-white text**: Components that use `background: "#fff"` (hardcoded white) with `color: "var(--ink)"` become invisible in dark mode because `--ink` resolves to `#f7f2ff` (near-white). Preferred fix: use CSS variables — `var(--card)` for card/input backgrounds, `var(--bg)` for page backgrounds. Check these files: PostCard.tsx, CreatePostPage.tsx, EditPostPage.tsx, PostsPage.tsx, DashboardPage.tsx.

  For catch-all fallback, `globals.css` has a broad selector that overrides any remaining hardcoded white inline styles in dark mode:
  ```css
  .dark [style*="background: #fff"],
  .dark [style*="background:#fff"],
  .dark [style*="background: #ffffff"],
  .dark [style*="background:#ffffff"],
  .dark [style*="background: white"],
  .dark [style*="background:white"],
  .dark [style*="background: #FFF"],
  .dark [style*="background: #FFFFFF"],
  .dark [style*="background:#FFFFFF"],
  .dark [style*="background-color: white"],
  .dark [style*="background-color:white"] {
    background: var(--card) !important;
  }
  ```
  Add new variants here when discovery shows white backgrounds not matched by existing selectors.
- **Comment GET blocks the response**: In `internal/comments/handler.go`, `syncInstagramComments()` was called synchronously on GET, making HTTP calls to Instagram's API (1-5s) before returning the comment list. MUST run as `go h.syncInstagramComments(...)` — the sync fetches from Instagram in the background while the local DB result is returned immediately.
- **Analytics includes non-published posts**: `analyticsOverview` passed ALL posts (SCHEDULED, FAILED, DRAFT) to `analyticsSummary()`, dragging averages to zero. Fix: filter to `status == "PUBLISHED"` before computing aggregates. Also, `analyticsRefresh` should call `comments.RefreshPostInsights()` (reach, impressions, saves) in addition to `RefreshPostMetrics()` (likes, comments).
- **Delete post doesn't cascade to platforms**: The DELETE handler only removed local DB rows. Must first look up `platform_post_id` from `post_targets` for PUBLISHED targets and call the platform's DELETE API: Instagram `DELETE /{ig-user-id}/media?access_token=...`, Facebook `DELETE /{page-id}_{post-id}?access_token=...`. Then clean up `post_targets`, `instagram_comments`, and `posts`.
