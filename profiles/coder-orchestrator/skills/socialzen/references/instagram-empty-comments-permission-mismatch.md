# Instagram empty comments permission mismatch

Use when `GET /<IG_MEDIA_ID>/comments` returns HTTP 200 with `{"data":[]}` and UI/pagination fixes have already been ruled out.

## Decisive audit sequence

1. Resolve the real provider identity from `post_targets.platform_post_id`; record the local post ID separately.
2. Call `GET https://graph.instagram.com/<version>/me?fields=id,username,account_type` with the stored Instagram User token.
3. Call `GET /<IG_MEDIA_ID>?fields=id,username,owner,media_type,media_product_type,permalink,timestamp,comments_count,like_count`.
4. Confirm token `/me.id == media.owner.id`; this proves account ownership without exposing the token.
5. Call `GET /<IG_MEDIA_ID>/comments?fields=id,text,username,timestamp,like_count&limit=100` and capture redacted URL, parameters, HTTP status, relevant headers, and body.
6. If the edge is empty but `comments_count > 0`, do not classify it as a legitimate empty result. Treat it as an authorization/provider inconsistency. For Instagram Login, Meta documents `instagram_business_basic` plus `instagram_business_manage_comments` for this edge.
7. Ask the user to reconnect the Instagram account so the current token receives the comment-management grant. Existing tokens do not gain newly approved/requested scopes automatically. If reconnect still fails for accounts outside app roles, verify Meta App Review/Advanced Access.

## Important provider behavior

- `GET /me/permissions` is not a readable scope-inspection endpoint for these Instagram User tokens and can return `(#100) Tried accessing nonexisting field (permissions)`.
- `debug_token` may reject the Instagram Login token/app combination and therefore is not always usable as scope evidence.
- Capability evidence remains valid: basic account/media reads succeeding while the owned media reports `comments_count > 0` and the comments edge returns zero isolates the failure to comment authorization/provider behavior.
- A normal `IMAGE` + `FEED` media object is supported. Live video comments are the documented unsupported case.
- Pagination is not the cause when the first page is empty; still verify the implementation begins at the un-cursored URL and follows `paging.next` for top-level comments and each comment's `/replies` edge.
- Facebook Page comments and Instagram media comments are separate provider objects. A cross-post needs independent Facebook synchronization through `graph.facebook.com/<FACEBOOK_POST_ID>/comments`; Facebook comments are not expected from the Instagram edge.

## Minimal product fix

When the Instagram comments edge returns zero, fetch `comments_count` for the same media. If it is greater than zero, return an actionable provider error instead of `empty`; preserve `empty` only when both counts are zero. Keep tokens redacted in every URL/body log.

Regression shape:

- `fetched=0`, `comments_count=5` => error mentioning the mismatch/reconnect.
- `fetched=0`, `comments_count=0` => legitimate empty status.
- Existing first-page, `paging.next`, reply pagination, and reconnect-account tests remain green.
