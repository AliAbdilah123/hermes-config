# Analytics Consistency Review Pattern

Use this when reviewing or implementing SocialZen Analytics ranking, thumbnails, nullable metrics, trend charts, refresh results, or “What Worked.”

## Source-of-truth rule

Analytics should have one provider-aware, nullable metric contract shared by overview cards, Top Posts, the table, trend chart, What Worked, post detail, and PDF export. Do not independently recompute engagement in the frontend.

- Preserve provider values as nullable: confirmed `0` is different from unavailable.
- A metric may be unavailable because the platform does not support it, Meta did not return/permit it for that target, or refresh failed.
- Do not describe unavailable as an Instagram-only-account limitation.
- If practical, expose the reason as `unsupported`, `not_returned`, or `refresh_failed`.

## Ranking and What Worked

- Top Posts should use the product-approved limit from the same filtered response; for the reviewed UX, show exactly Top 3.
- Best Post must be ranking position 1 under the active filters, using the canonical engagement value and deterministic tie-breaking.
- Highest Engagement references that same post.
- Best Content Type should use the highest average canonical engagement rate among qualifying posts and link to its strongest example.
- Best Posting Day & Time should use the highest average canonical engagement bucket, display the user's configured timezone, include sample size, and link to the strongest post in that bucket.
- Render the related thumbnail on every What Worked card and make the whole card an accessible control opening the existing post-detail modal.
- If no qualifying post exists, show `Not enough data` and disable navigation.
- Remove `Create a post like this` when it only copies caption/type; post-detail navigation is more useful and avoids encouraging shallow imitation.

## Thumbnail propagation

The frontend expects `mediaThumbnail`, but that alone does not prove Analytics supplies it. Trace the full boundary:

1. Analytics SQL selects primary ordered post media and media type.
2. Use `posts.media_thumbnail` only as a legacy fallback.
3. The row mapper populates `mediaThumbnail` and media type.
4. DTO serialization preserves both.
5. Image/video previews render appropriately in Top Posts, What Worked, table, and detail.

A common failure is `analyticsPosts()` copying `p["mediaThumbnail"]` while `analyticsRows()`/`analyticsMaps()` never selected or populated it.

## Trend semantics

The existing product model is post-derived activity: group published post-target facts by the post publication date in the user's timezone. Label it clearly, e.g. `Performance of posts published in this period`; it is not total account performance or performance observed on each calendar day.

- Daily buckets are appropriate through 90 days; weekly thereafter.
- Sum exact target facts once, then aggregate buckets.
- Keep unavailable nullable rather than initializing every absent metric to zero.
- For ISO-week Monday, do not use the second return value of Go's `ISOWeek()` as weekday—it is the week number. Use `Weekday()` with a Monday offset and test the resulting bucket date across month/year boundaries.
- Add separate account-level snapshots only when follower/profile growth or observation-date trends are explicitly required.

## Refresh result semantics

Refresh counts represent attempted published platform targets, not posts and not individual metrics.

- `refreshed`: all requested metrics for one target succeeded.
- `partial`: some calls/metrics succeeded and others failed.
- `failed`: no usable refresh succeeded for that target.

Prefer explicit copy: `12 platform targets checked · 0 fully refreshed · 6 partially refreshed · 6 failed`.

If the frontend sends `account_id`, verify the backend actually scopes the refresh; otherwise implement scoping or remove the misleading parameter. Offer expandable, credential-safe provider reasons.

## Review checklist

- Compare backend and frontend engagement formulas.
- Check whether null becomes zero in cards, table, trends, PDF, or sorting.
- Confirm Top Posts and Best Post cannot disagree.
- Confirm thumbnail/account identity fields are selected, mapped, and serialized.
- Test weekly bucket dates, not only the daily/weekly mode switch.
- Test account-scoped refresh behavior.
- Explain chart population and refresh counts in user-facing language.
- For review-only requests, publish the responsive SocialZen HTML review artifact and do not modify/deploy application behavior.
