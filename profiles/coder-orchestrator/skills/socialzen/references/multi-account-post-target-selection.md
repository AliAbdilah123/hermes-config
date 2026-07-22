# Multi-account post target selection

Use this when the post composer must publish one post to multiple connected accounts, including several accounts on the same platform.

## Contract

- Model composer selection as a generic ordered list: `targets: [{ platform, accountId }]`.
- Keep UI state as account-ID arrays keyed by platform, rather than one scalar account ID per platform.
- Checking a platform enables its account checklist; unchecking it clears only that platform's selected accounts.
- Require at least one selected account for every enabled platform and at least one target overall.
- Keep singular legacy fields (`instagramAccountId`, `facebookPageId`, `threadsAccountId`) only as a compatibility input path; new UI requests should send `targets`.
- Derive platform-level post-type/media restrictions from the distinct platforms represented in targets. Do not assume one target per platform.

## Backend trust boundary

Before reserving quota or creating the post:

1. Require `targets` to be an array of objects with non-empty `platform` and `accountId`.
2. Reject unsupported platforms explicitly.
3. Reject duplicate `(platform, accountId)` pairs.
4. Verify each account belongs to the authenticated user and is active in the platform-specific account table.
5. Resolve and persist the stable provider account ID for every target.

Insert quota reservation, parent post, media rows, and every `post_targets` row in one transaction. Check every `Exec` error and roll back the whole operation; never commit the parent post and then insert targets with ignored errors, because that can create an unschedulable orphan post while still returning success.

The legacy `posts.instagram_account_id` field may use the first selected Instagram account for compatibility. For a post with no Instagram target, use the existing schema-safe compatibility value only until that legacy column can become nullable; publishing identity must come from `post_targets`.

## TDD regression shape

Backend tests should prove:

- Two Instagram targets produce two `post_targets` rows for one post.
- Mixed Instagram/Facebook/Threads selections preserve all target account IDs.
- Empty, malformed, duplicate, unsupported, foreign-user, and inactive targets fail before post creation/quota reservation.
- A forced target insert failure rolls back the parent post and quota reservation.
- Legacy singular payloads still create the expected target while compatibility remains supported.

Frontend tests should cover the pure selection/payload helpers: independent same-platform toggling, deselection, stable target order, and flattening all selected accounts into `targets`.

## Verification

Run focused backend target tests, the posts package tests, frontend composer/helper tests, TypeScript checking, and both production builds. After deployment, verify the service health endpoint, app HTML, the deployed composer bundle marker, and public JavaScript `Content-Type: application/javascript` before reporting success.
