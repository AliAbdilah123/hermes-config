# Meta analytics permission validation

Use this when deciding whether SocialZen should request `instagram_manage_insights` or `read_insights` after users reconnect Instagram and Facebook.

## Decision rule

Run live calls with tokens issued by a clean reconnect. Add a permission only when Meta explicitly identifies that exact permission as missing for an analytics call SocialZen currently makes. Do not infer a scope requirement from unsupported metrics, invalid metric names, Page Public Content Access/app-access errors, or empty insight data.

## Evidence sequence

1. Confirm the reconnected account row is active, has a non-empty token, and has a newly updated expiry/connection timestamp.
2. Identify a published target belonging to that exact active account. A fresh token does not make a post from a disconnected account a valid test target.
3. Probe the exact production calls rather than broad capability endpoints:
   - Instagram media fields: `like_count,comments_count`
   - Instagram media insights: `reach,impressions,saved,shares` with `period=lifetime`
   - Facebook post fields: `likes.summary(true).limit(0),comments.summary(true).limit(0),shares`
   - Facebook post insights currently used by the code
4. Use Meta's token debugger where app credentials are available to verify validity and granted scopes. Do not print or document raw tokens.
5. Record HTTP status, Meta error code/message, returned metric names, token validity/scopes, and the least-privilege decision.

## Interpretation

- Instagram HTTP 200 for `reach,saved,shares` proves those current analytics work without `instagram_manage_insights` when that scope is absent.
- Meta error code 100 saying `impressions` is unsupported for the media product type is a metric-availability limitation, not a missing permission. Keep the existing retry without `impressions`.
- Facebook error code 10 requesting `pages_read_engagement` or Page Public Content Access is not evidence for `read_insights`, especially when token debugging confirms `pages_read_engagement` is granted. Treat it as app-access/feature review follow-up.
- Facebook error code 100 saying an insight metric is invalid is endpoint/version/metric compatibility, not a permission failure.
- An Instagram insights response containing only an `id` and no `data` is insufficient proof by itself. Retry the supported metric subset and another eligible published media item before deciding.

## Scope outcome

If neither provider explicitly reports `instagram_manage_insights` or `read_insights` as missing, leave OAuth scopes unchanged. Document separately any endpoint compatibility or App Review access issue; never use speculative scope expansion to mask it.

## Verification and reporting

Run focused OAuth scope tests after the audit even when no source changes are needed. If the full test suite has unrelated failures, report them separately and do not misstate the focused result. Commit only the audit documentation when the conclusion is “no scope change.”
