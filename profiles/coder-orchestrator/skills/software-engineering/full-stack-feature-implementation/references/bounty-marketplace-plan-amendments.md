# Bounty / gig marketplace planning amendments

Use this when planning or updating a PRD/review artifact for a two-sided bounty/gig marketplace where posters create work requests and workers submit proposals.

## Product-model pitfalls

- Do not invent a payment artifact from user bank details. If bank details are part of onboarding/profile, treat them as user-owned profile data only.
- A poster approves or declines **proposals**, not bank details or proposers' bank-detail records.
- If payments are manual/out-of-app, document that the app coordinates proposal state only; do not add payment-gateway flows or bank-detail exposure unless explicitly requested.

## Common requirements to capture explicitly

- Proposal eligibility gates can include both verified email and completed bank details.
- Gig statuses may be product-specific; preserve the user's exact labels (example: `unpublished`, `open_submission`, `closed_submission`, `finished`) rather than mapping to generic task statuses.
- Quota approval rules need explicit behavior:
  - approving over quota should warn first;
  - confirmed over-quota approvals should increase quota by the number of additional approvals;
  - declining approved proposals may optionally reopen submissions;
  - increasing quota may optionally reopen submissions.
- If gigs have a duration, add both backend fields and frontend UI requirements:
  - `start_at` and `end_at` datetime fields;
  - datetime picker in the create/edit form;
  - backend validation that `end_at > start_at` with a clear 400 error such as `valid_duration_required`.
- For image attachments, specify count, type, and size limits at both API and UI levels (example: one image per gig/proposal, max 5MB, image/jpeg|png|webp only).

## Review artifact update checklist

When the user corrects wording after reviewing a plan:
1. Update the canonical markdown/source plan.
2. Update the published HTML review artifact at the same public URL unless a new version is requested.
3. Verify the public artifact contains the new exact terms and no longer contains the rejected phrase.
