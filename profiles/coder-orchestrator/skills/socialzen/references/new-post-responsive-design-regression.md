# New Post Responsive Design Regression

Use when the user says the New Post/create form is not responsive or does not match the app design after a redesign/mockup pass.

## Root pattern

`CreatePostPage.tsx` lives inside the real app shell (`AppLayout` + desktop `Sidebar` + mobile `BottomNavigation`). A standalone full-screen mockup inside the route can fight the shell:

- hardcoded dark background/card colors no longer match the light app/sidebar theme;
- `min-h-screen`/centered fixed card wastes mobile height inside an already scrollable outlet;
- route-level footer/card wrappers can create cramped mobile scrolling and visual mismatch;
- removing `Topbar` makes the page inconsistent with the rest of the app.

## Smallest safe fix

Prefer the app-native responsive layout:

- render `<Topbar title="New Post" subtitle="Schedule content" />`;
- wrap content in `p-4 md:p-8 max-w-[640px]` instead of a full-screen centered mockup;
- use theme tokens (`var(--ink)`, `var(--card)`, `var(--line)`, `var(--violet-600)`) instead of one-off hardcoded dark colors;
- keep actions in the normal form flow (`flex flex-col sm:flex-row gap-3`) rather than a fixed/tall card footer;
- preserve mobile bottom-nav spacing from `AppLayout` rather than adding route-specific viewport hacks.

## Preserve account-selection fixes while reverting design

If reverting from a dark mockup back to the app-native layout, keep these fixes:

```ts
const instagramAccounts = accounts.filter(a => a.provider === "instagram")
const selectedInstagramAccount = instagramAccounts.find(a => a.id === accountId)
const selectedInstagramLabel = selectedInstagramAccount ? `Instagram — @${selectedInstagramAccount.igUsername || "connected account"}` : ""
```

Then pass the selected label into the trigger so it never shows `acct_*`:

```tsx
<SelectValue placeholder="Select Instagram account">{selectedInstagramLabel}</SelectValue>
```

Do not include `mock` or Facebook-derived rows in the Instagram selector; they make Instagram appear connected without explicit consent.

## Verification

- `pnpm typecheck`
- `pnpm build`
- deploy `dist/` to `/var/www/html/projects/socialzen/`
- verify the deployed `CreatePostPage-*.js` contains `provider==="instagram"` and `Instagram — @`
- verify the deployed chunk no longer contains standalone dark mockup copy such as `Schedule and manage your social content across platforms.` when reverting to the app-native page
