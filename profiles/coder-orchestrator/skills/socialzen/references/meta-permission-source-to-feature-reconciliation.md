# Meta permission source-to-feature reconciliation

Use this when a Meta scope audit claims a provider feature is deferred or absent, but similarly named backend helpers or shared frontend controls still exist.

## Reconciliation workflow

1. Inspect the exact active OAuth scope arrays and authorization-URL tests.
2. Trace every provider-specific Graph helper, including unreferenced/dead helpers. Dead code does not prove an active feature, but it contradicts an audit that says the capability is cleanly excluded and can be reactivated accidentally.
3. Trace the real invocation path separately. A helper definition without callers is dormant, not end-to-end implementation.
4. Inspect shared UI controls by target platform. A generic Comments button can expose Instagram mutation controls on Facebook posts even when Facebook moderation scopes are intentionally absent.
5. Choose one least-privilege state:
   - Complete the provider feature, request its proven minimum scope, disclose it, and add reviewer evidence; or
   - Remove/defer provider calls and gate the UI to the supported platform.
6. Reconcile OAuth, backend calls, frontend labels/gates, legal copy, tests, and audit documentation together. Avoid wording such as “deferred” while dormant provider code and actionable shared UI remain.

## SocialZen Facebook comment boundary

For the core Facebook tranche, keep only Page discovery, publishing, and engagement analytics unless Facebook comments become a separate production-ready feature. If `pages_read_user_content` and `pages_manage_engagement` are absent:

- no Facebook comment Graph reads should remain in the active/dormant provider sync path;
- the post-detail comment action should require a published Instagram target and identify itself as Instagram comments;
- App Review copy should state that Facebook comment reading/moderation is not implemented;
- focused OAuth tests should continue asserting the broader Facebook comment scopes are absent.

## Verification discipline

Run the repository's canonical command literally when completion checks require it, even if an equivalent direct binary invocation already passed. Also run focused OAuth/comment tests, backend build, frontend typecheck/build, public audit marker checks, and deployed JS content-type checks. Treat clean-token grants, Advanced Access, reviewer assets, and Meta Dashboard state as external proof, never source-level completion.
