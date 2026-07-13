# New Post account selection UX

When improving `apps/frontend/src/pages/posts/CreatePostPage.tsx` account/platform UX, keep this as a frontend UX-only layer unless the user asks for backend changes.

## Expected behavior

- If there are no connected Instagram accounts and no Facebook pages:
  - Show the warning text exactly: `Please connect a social account before creating a post.`
  - Provide connect actions that reuse existing OAuth helpers (`startInstagramConnect`, `startFacebookOAuth`).
  - Disable platform checkboxes and Post/Schedule actions.
- If connected accounts exist:
  - Do not auto-select a platform.
  - Keep all platform checkboxes unchecked by default (`platforms` starts as `[]`).
  - Only show/enable an account selector after its platform is selected.
- Never display internal account IDs such as `acct_*` in the UI.
  - Instagram option format: avatar/icon + `Instagram — @username`.
  - Facebook option format: avatar/icon + `Facebook — Page Name`.
- Prevent submit unless every selected platform has its corresponding account/page selected.

## Minimal implementation notes

- Remove single-account auto-selection in the `fetchInstagramAccounts()` effect.
- Derive `instagramAccounts`, `hasConnectedAccounts`, and `canSubmit` locally.
- Clear `accountId` / `fbPageId` when their platform is unchecked.
- Keep existing create-post payload and backend business logic unchanged unless explicitly requested.

## Verification

Run:

```bash
cd apps/frontend
pnpm typecheck
pnpm build
```

After deploy, verify the built CreatePost chunk contains the warning copy and returns `application/javascript` from the public URL.
