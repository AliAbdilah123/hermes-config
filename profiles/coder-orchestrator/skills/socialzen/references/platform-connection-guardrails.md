# Platform connection guardrails for New Post and failed retry

Use this when improving SocialZen platform availability, New Post platform chips, or Edit & Retry validation.

## Frontend pattern

- Keep a small explicit supported-platform type for the screen (currently `instagram | facebook` in `CreatePostPage.tsx`; do not invent Threads UI unless the page already exposes it).
- Derive connection state from live account/page API data:
  - Instagram: direct `instagram_accounts` rows with `provider === "instagram"`.
  - Facebook: active/saved `facebook_pages` rows.
- Refresh connections on page focus (`window.addEventListener("focus", refreshConnections)`) so OAuth/reconnect flow enables chips after returning to the tab without a manual refresh.
- Do not auto-select platforms. Connected only means selectable; user still chooses target platforms/accounts.
- For disconnected platform chips:
  - render the platform anyway,
  - disable/non-click it,
  - use a subtle dark overlay/dim state, not a fully gray disabled look,
  - set a title/screen-reader hint like `Connect your Facebook account to enable posting.`
- If no platforms are connected, show the exact warning style/copy requested by the user: `Please connect at least one platform before creating a post.`

## Failed post retry pattern

- On `EditPostPage.tsx`, fetch current Instagram/Facebook connections in addition to the post.
- Determine required platforms from `post.targets` (the original platforms used by the failed post), not from the currently connected platforms.
- Block `Save & Retry` when any required platform is missing and show specific copy:
  - Facebook: `This post requires a Facebook connection. Please reconnect your Facebook account before retrying.`
  - Instagram: use the grammatically correct article: `This post requires an Instagram connection...`
  - Multiple: join labels (`Instagram and Facebook`) and ask to reconnect those accounts.
- Keep the button disabled while the warning is present; do not send PATCH until resolved.

## Backend safety net

- `internal/posts.Handler.patchPost()` already resolves failed targets via `resolveFailedTargets()` and stable external provider IDs (`ig_user_id`, `page_id`, `threads_user_id`). Keep that path as the server-side source of truth.
- If a stale/bypassed frontend sends retry while a required provider target has no active matching connection, return a clear 400 with the same warning style. Preserve existing tests that check for reconnect wording.
- Do not loosen retry validation to “any account of same platform is connected”; for failed targets, same external provider account/page should be reconnected or the target should remain failed.

## Verification checklist

- Add/keep a small helper test for platform connection copy/state.
- Run:
  - `pnpm exec vitest run src/lib/platform-connections.test.ts`
  - `pnpm typecheck`
  - `pnpm build`
  - `go test ./internal/posts`
  - `go build -o /tmp/socialzen-api .`
- Deploy both frontend and backend when both changed.
- Verify the deployed JS asset is `application/javascript` and contains a distinctive retry-warning marker such as `This post requires`.
