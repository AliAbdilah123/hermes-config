# Cross-platform analytics provider enablement

Use when an already-supported publishing provider is missing or incomplete on Analytics.

## End-to-end audit

Treat provider support as a backend → DTO → frontend → export contract. Verify all of these independently:

1. The analytics overview validates the provider and scopes SQL by `post_targets.platform`.
2. Provider refresh fetches metrics and persists them to `post_target_metrics` for the exact target.
3. The shared analytics mapper carries the provider target, nullable metrics, media, and availability state.
4. Overview summaries and engagement-rate eligibility follow provider capabilities.
5. Trend buckets, ranking, details, and PDF consume the same normalized metrics.
6. The platform selector exposes the provider and sends its lowercase API value.
7. Refresh-result capability labels omit unsupported metrics rather than treating them as failed or zero.

## Capability-sensitive engagement

Do not require every shared metric column for every provider. In particular, Instagram supports Saves while Facebook and Threads do not. Engagement for Facebook/Threads can be computed from Likes + Comments + Shares when each supported component is measured; a null Saves value must not make the aggregate unavailable. For mixed-target posts, require Saves if any contributing target is Instagram.

Preserve the distinction between unsupported/unavailable and confirmed zero. Never coerce missing provider metrics to zero merely to make an aggregate calculable.

## Threads contract

Threads insights map:

- `likes` → Likes
- `replies` → Comments
- `views` → Reach and Impressions (until a distinct supported contract exists)
- `reposts + quotes` → Shares
- Saves → unsupported/null

The Analytics filter value is `threads`, displayed as `Threads`. Threads refresh capability labels are Likes, Comments, Reach, Impressions, and Shares.

## Verification

Add focused checks proving:

- the selector includes Threads and changing it requests `platform=threads`;
- the overview accepts and scopes `threads`;
- Threads engagement remains available when Saves is null;
- Threads insight parsing and persistence map the provider fields correctly;
- frontend analytics tests, typecheck, production build, focused Go analytics tests, provider tests, and Go build pass.

After deployment, inspect the public Analytics chunk (not only the source build) for the Threads option marker and verify JavaScript content type. An authenticated browser render is still required when credentials/session access are available. Do not describe bundle-marker inspection as full public E2E.
