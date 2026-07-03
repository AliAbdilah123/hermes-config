# SocialZen Facebook Page Crossposting (Go/SQLite stack)

Use this when implementing Meta/Facebook Page publishing features in the local SocialZen stack. The upstream plan may mention Cloudflare Worker/Drizzle/R2, but the deployed project currently runs a Go backend with SQLite and a Vite frontend.

## Durable implementation pattern

- Adapt schema tasks into `apps/backend-go/main.go:migrate()`:
  - `facebook_pages`: stores Page ID/name/username/category/picture, encrypted/encoded page token, token expiry, status.
  - `post_targets`: one row per platform target (`instagram`, `facebook`, future `threads`) with per-target status and platform post IDs/permalinks/errors.
  - Backfill existing Instagram posts with `INSERT OR IGNORE INTO post_targets ... SELECT ... FROM posts` so old IG-only posts get an Instagram target.
  - **⚠️ DO NOT run this backfill on every startup in `migrate()`.** The ID scheme in the backfill (`'pt_'||id`) differs from the app's runtime ID generation (`models.NewID("pt")` which produces random IDs like `pt_abc123`). Running `INSERT OR IGNORE` with mismatched IDs on every restart silently creates duplicate instagram targets for every post, so single-platform posts become cross-platform, and Instagram posts get double-published. Use the backfill once when creating the table, then remove it.
- Keep deprecated IG columns on `posts` for compatibility. In this stack `instagram_account_id` is still non-null, so FB-only posts need a compatibility fallback (usually `acct_demo`) until a later schema rebuild makes it nullable.
- Add indexes for target lookup: `post_id`, `(platform,status)`, `(platform,status,post_id)`, and `account_id`.

## OAuth/page discovery pattern

- Reuse Facebook Login OAuth start, but callback should save **all** pages from `/me/accounts`, not just pages with `instagram_business_account`.
- Request page fields like `id,name,username,category,picture{url},access_token,instagram_business_account{id,username,profile_picture_url}`.
- For every page, upsert into `facebook_pages` using Facebook Page names (not IG usernames).
- For pages with `instagram_business_account`, preserve existing Instagram account save behavior.
- Redirect with a Facebook-specific success indicator such as `connected=facebook&pages=N`.

## API/UI pattern

- Add `GET /api/facebook/pages` and `DELETE /api/facebook/pages/:id`; never return stored tokens.
- `POST /api/posts` should accept `platforms`, `facebookPageId`, and keep `instagramAccountId` for backward compatibility.
- Reject `TEXT` and `LINK` if Instagram is selected; they are Facebook-only.
- `GET /api/posts` and calendar/dashboard shapes should include `targets[]` alongside legacy `instagramAccount`.
- Settings UI must show Facebook Page data (`pageName`, category, picture, username) and must not show IG usernames or Instagram-only hashtag controls in the Facebook section.
- Create-post UI should include a platform selector, Facebook Page dropdown, FB-only `TEXT`/`LINK` types, and caption limits: 2,200 when Instagram is selected, 63,206 for Facebook-only.

## Threads integration extension

When adding Threads to SocialZen, adapt Cloudflare/Drizzle plans to the same local Go/SQLite stack:
- Add `threads_accounts` inside `apps/backend-go/main.go:migrate()` with app-scoped Threads user ID, username/name/avatar, encrypted token, expiry, status, and `UNIQUE(user_id,threads_user_id)`.
- Add `THREADS_APP_ID`, `THREADS_APP_SECRET`, and `THREADS_REDIRECT_URI` config aliases in `loadConfig()`; sign Threads OAuth state with the Threads secret/state secret, not the Instagram/Facebook secret.
- Register local routes in `dispatch()`: `/api/threads/oauth/start`, `/api/threads/oauth/callback`, `/api/threads/accounts`, and any rate-limit helper endpoint.
- Threads OAuth uses `https://threads.net/oauth/authorize`, `POST https://graph.threads.net/oauth/access_token`, optional `GET https://graph.threads.net/refresh_access_token?grant_type=th_refresh_token`, and `GET https://graph.threads.net/v1.0/me?fields=id,username,threads_profile_picture_url,name`.
- `POST /api/posts` should accept `platforms: ['threads']` and `threadsAccountId`, reject `REEL` for Threads, enforce the 500-character caption limit when Threads is selected, and insert a `post_targets(platform='threads')` row.
- In the local scheduler path, dispatch Threads through the 2-step container flow (`/{userId}/threads` then `/{userId}/threads_publish`) using public media URLs; the local stack may only have `media_thumbnail` available unless a richer post-media association is added.
- Frontend additions: `src/lib/threads.ts`, `ThreadsIcon`, a third Settings account card, Threads account selector and 500-char/link behavior in CreatePost, and target labels/colors in dashboard/calendar/post cards.

## Pitfalls

- **Photo `published=false` hides posts**: When posting photos to `/photos`, setting `published=false` uploads the photo but does NOT show it in the Page feed — the post is invisible to visitors. Use `published=true` (or omit the parameter; default is `true`). This is an easy silent bug: the API returns success (200 + post ID) but nothing appears on the Page.
- **New OAuth scopes need reconnect**: Adding `pages_manage_posts` or `pages_manage_metadata` after a user already connected their Facebook account means the existing token lacks those permissions. The user must disconnect and reconnect through the Settings UI to get a fresh token.
- **`INSERT OR IGNORE` backfill in `migrate()` creates duplicate targets**: If the backfill ID scheme (`'pt_'||id`) differs from the app's `NewID("pt")`, the `INSERT OR IGNORE` succeeds on every restart, silently adding duplicate instagram targets. Single-platform posts become cross-platform; Instagram posts get double-published. Run the backfill once when creating the table, then remove it from `migrate()`.
- **Threads OAuth saves to wrong table**: The generic `oauthCallbackGeneric` inserts into `instagram_accounts` for all providers. For Threads (`provider='threads'`), the account must be saved to `threads_accounts` instead. Without this guard, Threads connections land in `instagram_accounts` with a `threads` provider tag but no token, and the threads_accounts table stays empty.
- **Threads tokens expire in 1 hour by default**: Unlike Instagram/Facebook which exchange short-lived tokens for long-lived ones (~60 days), Threads' `exchangeThreadsCode` hardcoded a 1-hour expiry. Use the `th_exchange_token` grant type at `GET https://graph.threads.net/v1.0/access_token?grant_type=th_exchange_token&access_token=...` to get a long-lived token, same pattern as Instagram's `ig_exchange_token` and Facebook's `fb_exchange_token`.
- **Cross-platform partial success leaves post stuck**: When a post has multiple targets (IG + FB) and one succeeds while the other fails, the old publisher left the parent post as PUBLISHING forever (no retry, no failure). Fix: count already-published targets before the publish cycle. If any target already succeeded, set parent to FAILED with "Some platforms failed to publish" (not "All"). This makes the post visible in the Failed tab for Edit & Retry.
- **PATCH endpoint resets FAILED→SCHEDULED**: When saving a failed post via Edit & Retry, the PATCH handler should reset post status to SCHEDULED and clear error messages on both the post and its failed post_targets. Otherwise the publisher skips the post because it's still FAILED.
- **EditPostPage blocks FAILED posts**: The frontend guard `if (post.status !== "SCHEDULED")` blocked the edit form for all non-scheduled posts, including FAILED posts. The Edit & Retry button on PostCard navigated to the edit route but the user saw "Only scheduled posts can be edited" with no form. Allow `post.status === "FAILED"` in the guard.
- **PATCH handler doesn't update media_thumbnail**: The PATCH endpoint handled caption, publishAt, and analytics but silently ignored `media` array updates (thumbnail replacements). The edit form's "Ganti Media" flow uploads new media but the thumbnail never updated in the database.

- Backend: `go test ./...` from `apps/backend-go`.
- Frontend: `npm run typecheck`, `npm test -- --run`, `npm run build` from `apps/frontend`.
- Deployment: build Go binary from `apps/backend-go`, copy frontend `dist` to the nginx alias directory, restart `socialzen.service`, then curl the public page and `/projects/socialzen/api/health`.
- For SQLite in-memory tests using `database/sql`, shared-cache memory DBs avoid “no such table” errors from multiple pooled connections: `file:memdb_<test>?mode=memory&cache=shared`.