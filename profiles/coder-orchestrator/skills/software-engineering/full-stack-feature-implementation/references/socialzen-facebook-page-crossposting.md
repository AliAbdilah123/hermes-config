# SocialZen Facebook Page Crossposting (Go/SQLite stack)

Use this when implementing Meta/Facebook Page publishing features in the local SocialZen stack. The upstream plan may mention Cloudflare Worker/Drizzle/R2, but the deployed project currently runs a Go backend with SQLite and a Vite frontend.

## Durable implementation pattern

- Adapt schema tasks into `apps/backend-go/main.go:migrate()`:
  - `facebook_pages`: stores Page ID/name/username/category/picture, encrypted/encoded page token, token expiry, status.
  - `post_targets`: one row per platform target (`instagram`, `facebook`, future `threads`) with per-target status and platform post IDs/permalinks/errors.
  - Backfill existing Instagram posts with `INSERT OR IGNORE INTO post_targets ... SELECT ... FROM posts` so old IG-only posts get an Instagram target.
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

- Backend: `go test ./...` from `apps/backend-go`.
- Frontend: `npm run typecheck`, `npm test -- --run`, `npm run build` from `apps/frontend`.
- Deployment: build Go binary from `apps/backend-go`, copy frontend `dist` to the nginx alias directory, restart `socialzen.service`, then curl the public page and `/projects/socialzen/api/health`.
- For SQLite in-memory tests using `database/sql`, shared-cache memory DBs avoid “no such table” errors from multiple pooled connections: `file:memdb_<test>?mode=memory&cache=shared`.