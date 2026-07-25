# Terms persistence and platform-aware post account display

## Repeated Terms update card

When an authenticated user sees the Terms update gate after every reload, reconnect, or login:

1. Inspect the live `users.terms_version` and `users.terms_accepted_at` values before changing frontend state.
2. Compare them with `currentTermsVersion` in `apps/backend-go/legal_terms.go`.
3. A legacy account with `NULL` values is expected to remain gated until the user explicitly accepts. Do not backfill legal acceptance for ordinary users: that would falsely record consent.
4. Verify the acceptance endpoint updates both columns and the status endpoint subsequently returns `requiresAcceptance: false`.
5. Separate legacy users from new users. Email signup and first-time Google signup should persist the current version and timestamp from the signup consent contract, so new users should not receive an immediate update gate.
6. Check the live database distribution instead of generalizing from one account. Rows with current version plus a non-empty timestamp prove persistence; legacy `NULL` rows explain repeated prompts for those accounts.

Root-cause reporting should state whether the card is caused by missing persisted consent, a failed acceptance write, or a version mismatch. Do not describe a legitimate legacy consent gate as a frontend reload bug.

## Post Card and Post Detail account consistency

Post account labels must derive from `post.targets`, not from the legacy parent `post.instagramAccount` field:

- Instagram: `@target.accountUsername`
- Facebook: `Facebook: target.pageName`
- Threads: `Threads: @target.threadsUsername`
- Cross-posts: format every target independently in target order
- Legacy posts with no targets: only then fall back to `post.instagramAccount.username`

Keep one small shared frontend formatter (for example `postAccountLabel(post)`) and use it in both Post Card and Post Detail. This prevents Facebook-only posts from showing an Instagram demo fallback and keeps future Threads/cross-post behavior aligned.

Regression coverage should include:

1. A Facebook-only post whose legacy Instagram username is deliberately different; assert only the Page name is shown.
2. A cross-post with Instagram, Facebook, and Threads targets; assert each platform-specific identity appears independently.
3. The shared helper is consumed by both card and detail views rather than duplicating conditional formatting.

Verification: run the focused formatter/component test, frontend typecheck, build, deploy, and confirm the deployed Posts chunk is JavaScript and contains the platform-label marker. If the public CDN probe is transiently unavailable, verify the origin artifact but report the public boundary separately rather than claiming full public verification.