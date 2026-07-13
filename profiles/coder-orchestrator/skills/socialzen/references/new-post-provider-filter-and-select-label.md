# New Post provider filtering and Select label fallback

## Trigger

Use this when the New Post form appears to auto-connect Instagram, shows Instagram as available after the user disconnected it, or the Instagram account selector displays an internal `acct_*` id instead of a username.

## Root causes seen

- `CreatePostPage.tsx` treated non-direct rows as Instagram accounts, for example filtering with `provider === "instagram" || provider === "mock" || provider === "facebook"`.
- Facebook-linked/derived account rows can then make Instagram look connected even when the user has not explicitly connected Instagram.
- The shadcn/base Select trigger can fall back to the raw item `value` when the selected item content is complex JSX, so users see `acct_*` instead of `@username`.

## Minimal fix

In `apps/frontend/src/pages/posts/CreatePostPage.tsx`:

1. Only direct Instagram rows should populate the Instagram selector:

```ts
const instagramAccounts = accounts.filter(a => a.provider === "instagram")
```

2. Keep `platforms` initially empty and clear account ids when a platform is unchecked.
3. Render an explicit selected label in the trigger from the selected account:

```tsx
const selectedInstagramAccount = instagramAccounts.find(a => a.id === accountId)
const selectedInstagramLabel = selectedInstagramAccount
  ? `Instagram — @${selectedInstagramAccount.igUsername || "connected account"}`
  : ""

<SelectValue placeholder="Select Instagram account">{selectedInstagramLabel}</SelectValue>
```

4. Do not change backend payload/business logic unless the bug proves backend state is wrong. This is usually a frontend provider-filter + display-label bug.

## Verification

- `pnpm typecheck && pnpm build`
- Grep the built CreatePostPage chunk for both markers:
  - `provider==="instagram"`
  - `Instagram — @`
- Deploy frontend and verify the deployed chunk returns `Content-Type: application/javascript`.
