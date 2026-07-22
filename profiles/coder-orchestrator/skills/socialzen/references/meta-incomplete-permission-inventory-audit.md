# Meta incomplete-permission inventory audit

Use this reference when Meta Testing shows a list of incomplete permissions/scopes and the user asks for a full audit, not merely the permissions already used by SocialZen.

## Audit boundary

1. Transcribe **every item shown in Meta Testing** exactly, including product-level access labels such as Public Content Access, Human Agent, oEmbed Read, and Marketing API Access Tier.
2. Do not limit the matrix to scopes currently present in OAuth arrays or features currently exposed in the UI.
3. For each item, separate four facts:
   - Meta's intended capability;
   - whether SocialZen requests it in OAuth;
   - whether source code actually calls APIs that depend on it;
   - whether a reviewer-visible end-to-end feature exists.
4. Classify every item using exactly one requested status:
   - **Already used correctly** — requested, exercised by production code, and exposed through a legitimate user workflow;
   - **Related feature exists but scope is not utilized** — the product capability exists or substantially overlaps, but this exact scope is absent/unwired;
   - **Recommended future feature** — useful roadmap fit, but no complete current workflow;
   - **Not needed and should be removed** — no proportionate SocialZen use case, duplicate/legacy access, or unjustified review burden.
5. Dashboard access/approval state cannot be proven from source. Label it **Meta-dashboard verification required** rather than guessing.

## Evidence workflow

- Inspect actual scope arrays and generated authorization URL tests first.
- Trace provider calls to endpoints and fields; UI copy alone is not implementation evidence.
- Check whether onboarding is enabled. Backend-only code with a disabled connection flow is not reviewer-ready.
- Distinguish similarly named products/scopes and legacy/current variants. Meta Testing labels may not equal the direct Instagram Login scope names used by SocialZen (for example `instagram_manage_comments` versus `instagram_business_manage_comments`). Record the relationship, but never claim equivalence without checking the exact App ID/product/API version in Meta's current documentation/dashboard.
- Treat `email` and `public_profile` from Facebook Login separately from SocialZen's own email/password or Google login. Existing local user fields do not justify requesting Facebook `email`.
- Treat product access labels (Public Content Access, Human Agent, oEmbed, Marketing Access Tier) as capabilities with their own reviewer proof; do not silently fold them into OAuth scopes.

## Decision discipline

- Existing publishing, analytics, comments, replies, deletion, or account-discovery code can justify only the narrow permissions actually required by those calls.
- Do not invent features solely to retain a permission. Recommend removal when the roadmap value is weak or the same outcome is available with already-approved least-privilege access.
- Future-feature proposals must be practical for SocialZen (composer, inbox, moderation, analytics, listening, discovery, commerce tagging) and state the minimum UI, backend, policy, test fixture, and reviewer proof needed before requesting access.
- If two incomplete labels overlap one current feature, classify each independently; do not mark both used merely because one related scope is active.

## Required report outputs

Produce a complete platform-grouped matrix covering Facebook/Pages, Instagram, Threads, Embeds, and Marketing API. Each row must include purpose, current SocialZen evidence, gap/change, classification, and recommendation. Then provide:

- High / Medium / Low implementation roadmap;
- permissions to test immediately with clean tokens and real fixtures;
- permissions to submit for App Review now versus later;
- permissions to remove for least privilege;
- explicit dashboard-only uncertainties.

For SocialZen, publish this as a responsive dark/light HTML review artifact under `/prd/socialzen/`, preserve the canonical source under `docs/`, verify local and public HTTP 200, commit/push only the intended artifact, and state that the audit does not authorize product or dashboard changes.
