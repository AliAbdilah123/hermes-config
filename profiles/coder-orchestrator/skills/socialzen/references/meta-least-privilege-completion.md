# Meta least-privilege completion after an approved audit

Use this when a SocialZen Meta permission audit has been approved and the user asks to implement it, exclude unsupported products, and record what was done afterward.

## Completion sequence

1. Re-audit the current branch and recent commits before editing. An audit artifact can lag behind code; distinguish already-completed scope cleanup from remaining work.
2. Build an exact active-tranche contract across four layers:
   - OAuth scope arrays and generated authorization URLs;
   - backend Graph calls/routes;
   - reviewer-visible frontend workflows and pre-OAuth copy;
   - legal/App Review documentation.
3. Keep only scopes backed by a complete visible feature. For the narrow Facebook/Instagram tranche, keep conditional insights scopes absent until a newly issued clean token returns an explicit permission error and Meta confirms the exact scope for the configured product.
4. Exclude unsupported providers at every creation boundary, not only in UI:
   - remove/disable OAuth start and callback routes;
   - reject new provider targets in both legacy `platforms` and explicit `targets` request shapes;
   - retain historical account listing/disconnect only when needed for cleanup;
   - add route and target rejection tests.
5. If a related provider feature is incomplete, defer its API path rather than requesting a broader permission. Example: stop Facebook comment sync while preserving Instagram comment sync instead of adding `pages_read_user_content` or `pages_manage_engagement` without a complete Facebook moderation experience.
6. Correct onboarding copy to the actual OAuth product. Direct Instagram Login must not claim that a Facebook Page, Page admin role, or Facebook login is required.
7. Put a concise “What SocialZen will access” explanation before OAuth and align Terms/Privacy copy to the same active tranche. Remove active Threads, messaging, or deferred-scope claims.
8. After implementation, reconcile the existing public audit row by row in every supported language. Do not merely prepend a generic “implementation update” while leaving stale future-tense classifications below it. For every permission or product-access row, show separately:
   - feature implementation: implemented, partial, absent, or excluded;
   - OAuth request state: requested, intentionally withheld, or absent;
   - application evidence across OAuth, backend Graph calls/routes, reviewer-visible UI/copy, and focused tests;
   - external proof still required: clean-token grants, real reviewer fixtures, and Meta Dashboard state.
   Include a compact scoreboard whose counts agree with the matrix. A permission is not “complete” when only scope cleanup or documentation changed, and source implementation is not App Review completion.

## Verification

- Focused authorization-URL tests assert required scope presence and explicit deferred/unused scope absence.
- Focused tests cover disabled provider routes, both post-target payload shapes, provider-sync deferral, onboarding copy, and legal disclosure.
- Run backend focused tests/build and frontend focused tests/typecheck/build.
- Deploy backend, frontend, and the updated audit together when all were changed.
- Verify service health, public audit marker/HTTP 200, and deployed JS `Content-Type: application/javascript`.
- Commit and push only intended files; preserve unrelated dirty-tree artifacts.
- If the full suite has unrelated failures, report them separately and still run the narrow permission/OAuth suites plus the build. Never use an unrelated failure to blur the status of the audit update.

## Evidence boundary

Authorization-URL tests and source inspection do not prove Advanced Access, granted token scopes, reviewer roles/assets, redirect allowlists, app mode, business verification, or Meta Dashboard configuration. Clean-token end-to-end proof requires fresh Facebook and Instagram tokens plus real reviewer fixtures. Report this as remaining external verification, not as a completed test and not as a reason to add speculative scopes.
