# Threads permission source audit

Use this when mapping Meta Threads permissions to SocialZen implementation and App Review readiness.

## Audit method

For every listed permission, report five separate facts with exact `file:line` evidence:

1. **Requested OAuth scope** — inspect `threadsScopes` and prove the scope list is passed into OAuth start/callback. Do not infer requested scopes from comments, legal copy, dashboard configuration, or feature names.
2. **Existing product surface** — identify visible UI, routes, target validation, persistence, and tests. Treat these as feature intent, not proof of provider implementation.
3. **Actual provider API call** — find the concrete `graph.threads.net` endpoint, HTTP method, fields/metrics, token source, and caller. A data model or dispatch branch is not API usage.
4. **Gap/reviewer path** — trace the full path from connection through action to observable result. Check whether onboarding is disabled, dispatch supports Threads, published provider IDs can be created, and tests exercise the real endpoint.
5. **Classification** — distinguish:
   - requested + used + reviewer-accessible;
   - requested + used but reviewer path blocked/partial;
   - requested but unused/over-scoped;
   - not requested + unimplemented;
   - product surface exists but provider implementation is missing/broken.

## SocialZen findings captured July 2026

- Requested scopes are `threads_basic`, `threads_content_publish`, `threads_read_replies`, `threads_manage_replies`, and `threads_manage_insights` (`apps/backend-go/instagram_oauth.go:97-112`). OAuth start/callback consume that list at `instagram_oauth.go:807-817` and `823-830`.
- `threads_manage_insights` has concrete post-insights usage: `GET /{media-id}/insights?metric=views,likes,replies,reposts,quotes` and target-metric persistence (`apps/backend-go/internal/threads/metrics.go:15-31`, `42-69`). It requires an already-published Threads target/provider media ID.
- Threads target selection and validation exist (`apps/frontend/src/pages/posts/CreatePostPage.tsx:61-63`, `630-642`; `apps/backend-go/internal/posts/handler.go:164-238`), but publishing dispatch handles only Facebook and Instagram and otherwise returns `unknown platform` (`internal/posts/publisher.go:221-268`). Therefore `threads_content_publish` is requested but not implemented end-to-end.
- No Threads reply read/manage client exists. The insights metric named `replies` is only an aggregate count and is not evidence for `threads_read_replies`. Instagram comment routes must not be misclassified as Threads reply functionality.
- Provider-side Threads post deletion is absent: post deletion handles Instagram and Facebook only before local cleanup (`internal/posts/handler.go:349-384`). Local deletion is not Threads API deletion evidence.
- New Threads connections are disabled in Settings (`apps/frontend/src/pages/settings/SettingsPage.tsx:418-432`, `571-576`), although backend OAuth routes exist (`apps/backend-go/routes.go:143-148`). This blocks a reproducible App Review path even for implemented insights.
- The OAuth test checks only a subset of scopes and URL construction (`apps/backend-go/threads_test.go:50-75`); it does not prove permission use or provider behavior.

## Permission-specific interpretation pitfalls

- Own-profile `GET /me` supports `threads_basic`; it is not profile discovery.
- Multi-target scheduling to Threads and Instagram is not Threads `share_to_instagram` usage.
- Local keyword/hashtag history is not Threads keyword-search API usage.
- UI copy such as “publish,” “analytics,” or “manage replies” is intent, not API evidence.
- A scope comment is not evidence that a feature exists.

## Output shape

Use a compact permission matrix with columns: permission, feature/code, requested scope, actual API usage, gap, and likely classification. Lead with the exact requested-scope set, then close with least-privilege disposition and cross-cutting reviewer blockers. State explicitly that the audit was read-only and whether runtime/API verification occurred.
