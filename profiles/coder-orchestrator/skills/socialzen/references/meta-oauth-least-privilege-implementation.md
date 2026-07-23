# Meta OAuth least-privilege implementation

Use after a source audit has approved implementation of SocialZen’s current Meta App Review tranche.

## Scope-to-feature rule

Keep a scope only when production code performs the dependent API call and a reviewer can complete the corresponding user-visible workflow. Do not retain a scope merely because it may help asset discovery or analytics; prove necessity with a newly issued clean token first.

Current narrow tranche:

- Instagram: `instagram_business_basic`, `instagram_business_content_publish`, `instagram_business_manage_comments`.
- Facebook Pages: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`.
- Exclude Threads from this tranche.

Conditional scopes:

- Add `read_insights` only if a clean Facebook Page analytics test under the three Page scopes returns an explicit permission requirement.
- Add `instagram_manage_insights` (or the exact direct-Instagram product equivalent Meta identifies) only if clean-token media-insights testing proves it is required.
- Retain `business_management` only if clean-token `/me/accounts` testing proves a supported Business-owned Page cannot be discovered without it.

Never request yet: `pages_manage_engagement`, Instagram Public Content Access, Upcoming Events, oEmbed, Marketing API access, branded-content, or shopping permissions until each has its own complete production workflow and reviewer proof.

## Minimal implementation

1. Update scope arrays in `apps/backend-go/instagram_oauth.go`; remove unsupported scope comments too.
2. Add exact authorization-URL regression tests in `apps/backend-go/main_test.go`:
   - assert every required scope is present;
   - assert deferred/unused scopes are absent.
3. Update `apps/frontend/src/pages/legal/LegalPages.tsx` so its exact permission list and feature claims match OAuth. Remove messaging, Threads, or Business Portfolio claims from the active tranche when they are not requested.
4. Build/test backend and frontend, deploy both when touched, and verify the public JS asset content type.
5. Require reconnect after scope changes; existing tokens do not gain or shed grants automatically.

## Verification boundaries

- A focused OAuth URL test proves generated scope composition, not Meta Advanced Access or live token behavior.
- Source inspection proves API usage, not that Meta’s configured App ID/product grants it.
- Record clean-token evidence separately for Page discovery, Page publishing, Page analytics, Instagram publishing, Instagram comments, and Instagram insights.
- Do not claim end-to-end permission verification without reviewer/test Meta credentials and observable provider results.

## Pitfalls

- Legal copy can remain over-scoped after OAuth is corrected; treat it as part of the same change.
- A broad full Go suite may contain unrelated failures. Run focused scope tests first, then report broader failures precisely without weakening focused evidence.
- Do not add similarly named legacy and direct-Instagram permission variants together merely to satisfy a Meta Testing row; identify the exact product family first.
