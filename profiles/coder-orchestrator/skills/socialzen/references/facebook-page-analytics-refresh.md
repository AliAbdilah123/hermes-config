# Facebook Page analytics refresh

Use this when adding or debugging Facebook metrics in SocialZen analytics/post performance.

## Provider mapping

SocialZen stores post analytics in the shared `posts` columns used by the frontend:

- `likes`
- `comments`
- `reach`
- `impressions`
- `saves`
- `shares`

Facebook Page posts should update the same columns so the existing Analytics page and Post Detail Performance panel work without frontend duplication.

Facebook does **not** expose an Instagram-style saved/bookmark count for Page posts. Keep `saves` as `0` for Facebook instead of inventing a value.

## Graph API calls

For a published Facebook target, use `post_targets.platform_post_id` plus the connected Page token from `facebook_pages.access_token_encrypted`.

Engagement endpoint:

```text
GET https://graph.facebook.com/{version}/{platform_post_id}?fields=likes.summary(true).limit(0),comments.summary(true).limit(0),shares&access_token={page_token}
```

Map response:

- `likes.summary.total_count` -> `posts.likes`
- `comments.summary.total_count` -> `posts.comments`
- `shares.count` -> `posts.shares`

Insights endpoint:

```text
GET https://graph.facebook.com/{version}/{platform_post_id}/insights?metric=post_impressions,post_impressions_unique&period=lifetime&access_token={page_token}
```

Map response:

- `post_impressions_unique` -> `posts.reach`
- `post_impressions` -> `posts.impressions`

If insights are unavailable for a post type/token, do not fake reach/impressions. Preserve the existing safe failure behavior used by Instagram insights where possible.

## Integration points

Wire Facebook refresh anywhere Instagram metrics refresh is used for published posts:

- `apps/backend-go/analytics.go` `/api/analytics/refresh`
- `apps/backend-go/internal/posts/handler.go` per-post refresh
- `apps/backend-go/internal/sync/handler.go` sync action

Make the provider refresh succeed if **either** Instagram or Facebook refresh succeeds for the post. Cross-platform posts can have both targets; Facebook-only posts must not fail just because Instagram lookup fails.

## SQLite single-connection pitfall

Production uses `SetMaxOpenConns(1)`. Do not call provider refresh functions or other DB helpers while iterating an open `Rows`. First collect post IDs into a slice, close `rows`, then perform refreshes. Otherwise the sync endpoint can self-block waiting for the only DB connection.

## Minimal tests

At least test JSON parsing helpers for Facebook engagement and insights responses. A full live Graph test is not appropriate without credentials.
