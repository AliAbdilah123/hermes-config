# Explainable opportunity tags instead of arbitrary scores

Use this pattern when a product/CRM/lead-intelligence app has a vague numeric score that the user says is not actionable.

## Core product lesson

A numeric score often hides the reason a lead is useful. Replace or de-emphasize it with explicit, human-readable tags that describe extractable opportunity points, for example:

- `No Website` — website/landing-page offer.
- `Landing Page Offer` — simple conversion page with WhatsApp CTA.
- `WhatsApp Ready` — phone exists; outreach automation can start.
- `Website Audit` — existing site can be audited for SEO/speed/mobile/CTA.
- `Local SEO` — Maps/Google Business/Profile/review optimization angle.
- `Catalog Opportunity` — furniture/interior/product/service catalog angle.
- `Review Trust` — strong reviews can become social proof.
- `IKN Expansion`, `Commercial Interior`, `High-Value Service` — positioning and higher-ticket signals.
- `Needs Data Enrichment` — missing phone/address/website/etc.

## Implementation checklist

1. Update the review/PRD artifact first so the corrected product concept is visible, using the user's exact wording such as `Potential Tags`.
2. Add backend storage/API support for `potential_tags` while keeping legacy `score` only for backward compatibility if needed.
3. Add a deterministic tag rule engine that derives tags from website/phone/category/name/address/notes/enrichment fields.
4. CSV import should accept optional `potential_tags`; if absent, auto-generate tags.
5. Update list/detail/opportunity endpoints to return tags and sort by tag count or tag filters rather than score.
6. Replace frontend score UI with tag chips across dashboard, database table, opportunity page, CRM/detail modal, and edit form.
7. Rename score-based copy: e.g. `Avg. Skor` → `Avg. Potensi`, `Opportunity Engine` → `Potential Engine`, `Rules Scoring` → `Potential Tags`.
8. Verify with tests plus public deployed bundle/API checks that new copy exists and old score-forward copy is gone.

## Verification examples

- Backend unit test: business with no website + phone + catalog/review notes returns `No Website`, `Landing Page Offer`, `WhatsApp Ready`, `Catalog Opportunity`, `Review Trust`.
- API smoke: `/businesses` returns `potential_tags` as an array.
- Frontend bundle smoke: contains `Potential Tags` / `Avg. Potensi`; does not contain `Skor Peluang`.

## Pitfall

Do not just rename `score` to `potential`. The value comes from exposing concrete opportunity reasons, not from another hidden numeric ranking.