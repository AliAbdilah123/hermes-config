# Meta App Review readiness

Use this reference when planning or implementing Meta App Review preparation for SocialZen.

## Audit before changing code

Inspect the actual OAuth authorization URLs, backend scopes, reviewer-visible UI flows, legal disclosures, disconnect/deletion behavior, tests, and live canonical URLs. Separate application work from Meta Dashboard configuration; approval, Advanced Access, reviewer roles/assets, redirect allowlists, and product-specific deletion settings cannot be proven from source code alone.

Build a permission-to-feature matrix. Every requested permission must have:

1. A reviewer-visible entry point.
2. A complete end-to-end action and observable result.
3. Matching pre-OAuth and legal explanations.
4. A dedicated fixture/account the reviewer can access.
5. A focused authorization-URL regression test.

Remove or defer scopes without a demonstrable feature. Do not claim internally present but externally disabled providers in the current review tranche.

## Current SocialZen baseline

- Direct Instagram Login is separate from Facebook Page Login. Do not tell users that Instagram must be linked to a Facebook Page when the implemented OAuth product does not require it.
- Core Instagram candidates: `instagram_business_basic`, `instagram_business_content_publish`, and `instagram_business_manage_comments`.
- Core Facebook Page candidates: `pages_show_list`, `pages_read_engagement`, and `pages_manage_posts`.
- `instagram_business_manage_messages` has no reviewer-visible inbox/DM feature and should be removed unless that feature is actually implemented.
- `business_management` should be retained only if a clean-token asset-discovery test proves it is needed for a supported Business-owned Page.
- `pages_read_user_content` is conditional on retaining and proving Facebook user-comment reading. Do not request `pages_manage_engagement` without a reliable reviewer-visible Facebook moderation/reply flow.
- Threads onboarding is disabled in Settings, so exclude Threads permissions from the current submission even though backend support exists.

## Minimal implementation sequence

1. Audit Meta App IDs/products, modes, Advanced Access, redirect URIs, reviewer roles/assets, and deletion configuration without recording secrets.
2. Fix canonical legal/deletion URLs so dashboard URLs return direct HTTPS 200 responses without an HTTPS-to-HTTP redirect.
3. Align OAuth scope arrays, legal copy, and exact presence/absence tests.
4. Correct Settings prerequisites and add a compact “What SocialZen will access” explanation linked to identity, publishing, analytics, and comments.
5. Make OAuth denial, missing permission, and zero-Page outcomes specific and actionable; never report a successful Facebook connection when no Page was returned.
6. Clarify provider-specific comment capabilities in shared UI or defer ambiguous Facebook comment behavior.
7. Create a secret-free reviewer runbook mapping each permission to navigation, fixture, action, expected result, and recovery step.
8. Record screencasts only after clean-token live proof; regenerate the final scope list from the real authorization URL immediately before submission.

## Deletion boundary

SocialZen already provides public deletion instructions and authenticated account deletion. Confirm whether the exact Meta product accepts an instructions URL or requires a signed-request callback. Do not build a callback speculatively. If required, validate the signed request and return a public confirmation/status URL that exposes no personal data.

## Verification

Run focused OAuth URL tests, legal/settings UI tests, frontend typecheck/build, backend build/tests, live OAuth-start probes, direct HTTPS checks for privacy and deletion URLs, and clean reviewer-account walkthroughs. Distinguish pre-existing suite failures from regressions, but repair stale expectations owned by the OAuth changes before submission.

## Planning artifact rule

For a new Meta review-readiness request, follow SocialZen’s plan-first workflow: publish the responsive dark/light review artifact under `/prd/socialzen/`, verify local and public HTTP 200, commit and push the artifact, and explicitly state that application implementation/deployment has not happened until approved.
