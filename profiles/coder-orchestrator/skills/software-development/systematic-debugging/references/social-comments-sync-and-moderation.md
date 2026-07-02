# Social Comment Sync + Moderation Triage

Use when a social scheduler/comment-management UI has stale Instagram comments, local replies/likes that do not appear on Instagram, or missing moderation actions.

## Root-cause checks

1. Distinguish local comment state from provider state.
   - Local tables such as `instagram_comments` and `comment_likes` may only mirror UI state.
   - Provider-visible actions need the provider comment/media id and an access token with comment-management scopes.

2. Persist provider IDs for future actions.
   - When creating a top-level comment via Graph (`/{media-id}/comments`), store the returned Instagram comment id.
   - When creating a reply via Graph (`/{comment-id}/replies`), store the returned reply id.
   - Without this mapping, future reply/like/unlike/delete calls can only affect local state.

3. Sync before listing.
   - Before returning the comment-management list, fetch the latest provider comments and nested replies with fields like `id,text,username,timestamp,like_count,replies{id,text,username,timestamp,like_count}`.
   - Upsert by provider comment id into local storage and preserve `parent_id` for replies.
   - Return local rows after sync so the UI includes both provider-fetched and just-created local rows.

4. Likes and delete must call provider endpoints, not only update local UI.
   - Like: `POST /{comment-id}/likes`.
   - Unlike: `DELETE /{comment-id}/likes`.
   - Delete: `DELETE /{comment-id}`.
   - Local optimistic UI is fine, but server handlers should make best-effort provider calls when an Instagram comment id is known.
   - Frontend LikeButton should accept `likeCount` and optimistically increment/decrement on click, rolling back on error.

5. UI layout pitfall.
   - If a post-detail modal contains media, performance metrics, and comments, keep performance in a stable side panel next to the media on desktop.
   - Open comments as a right-side dialog/drawer on desktop so it does not cover the performance panel; keep single-column behavior on mobile.

## Verification

- Add a narrow provider-helper test using an HTTP test server to assert method/path for comment, reply, like, unlike, and delete helpers.
- Build the backend binary and frontend bundle that are actually deployed.
- Restart the deployed service and smoke-test `/api/health` plus the public SPA asset URL.

## Caveats

- Provider calls are often best-effort after local persistence; report provider failures explicitly when the product needs strict consistency.
- Existing comments created before provider-id persistence may not support reply/like/delete on Instagram until they are re-synced from Instagram or re-created.