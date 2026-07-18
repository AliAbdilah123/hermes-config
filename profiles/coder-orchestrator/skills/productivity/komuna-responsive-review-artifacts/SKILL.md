---
name: komuna-responsive-review-artifacts
description: Use when creating Komuna plans, PRDs, specs, or review HTML artifacts. Ensure the published review page itself is mobile-readable, responsive, and visually aligned with Komuna's website/dashboard theme.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [komuna, review-artifacts, responsive, html, planning]
    related_skills: [plan, komuna-operations]
---

# Komuna Responsive Review Artifacts

## Overview

Komuna review artifacts are not just source documents. The user reviews them on the public PRD route, often from mobile. Any plan, PRD, spec, or design proposal published for Komuna must be readable on phones and must look like it belongs to Komuna.

This skill applies to the **review artifact page itself** (`/prd/<name>.html`), not only to the feature being planned.

## When to Use

Use when:
- Creating or updating a Komuna plan, PRD, spec, or review document.
- Publishing HTML under `docs/*.html` and `/usr/share/nginx/html/prds/*.html`.
- The user asks for a public review link for Komuna.
- Updating an existing public Komuna review artifact after user feedback.

Do not use this as permission to implement the planned product feature. A review artifact remains a review artifact unless the user explicitly asks to implement/deploy the feature.

## Required Review Page Behavior

Every Komuna review HTML page must:

1. Include `<meta name="viewport" content="width=device-width, initial-scale=1" />`.
2. Use a responsive outer width such as `width:min(100% - 20px, 1120px)` instead of fixed desktop widths.
3. Collapse any desktop sidebar/table-of-contents into a single-column or two-column mobile layout.
4. Avoid horizontal overflow from tables, code blocks, wide grids, long URLs, or long headings.
5. Make code blocks horizontally scrollable with `overflow-x:auto` and `-webkit-overflow-scrolling:touch`.
6. Make tables mobile-readable: either convert rows to cards under small breakpoints or wrap them in a scroll container.
7. Use readable mobile font sizes: body text around 15–16px minimum; headings should use `clamp()`.
8. Keep tap targets and TOC links comfortably spaced on mobile.
9. Verify the public URL with a cache-busting query string after changes.

## Komuna Theme Requirements

Use Komuna dashboard-style visual language:

- Dark paper backgrounds: `--paper-1`, `--paper-2`, `--paper-3`.
- Warm ink colors: `--ink-1`, `--ink-2`, `--ink-3`.
- Subtle rules/borders: `--rule`, `--rule-2`.
- Accent color: `--accent`, `--accent-soft`.
- Serif large headings, mono uppercase eyebrows/labels, rounded cards, subtle borders.

Do not introduce:
- A generic blue SaaS theme.
- Bright white pages unrelated to Komuna.
- Tiny desktop-only tables on mobile.
- Fixed sidebars that consume most mobile width.
- Raw unstyled markdown dumps.

## CSS Pattern

A safe baseline:

```css
:root {
  --paper-1:#17120f; --paper-2:#211a16; --paper-3:#2d241e;
  --ink-1:#f7efe5; --ink-2:#d2c3b4; --ink-3:#9e8d7c;
  --rule:#3a2d26; --rule-2:#564238;
  --accent:#d86f45; --accent-soft:rgba(216,111,69,.16);
}
* { box-sizing: border-box; }
body { margin:0; background:var(--paper-1); color:var(--ink-1); line-height:1.65; }
.wrap { width:min(100% - 20px, 1120px); margin:0 auto; }
.layout { display:grid; grid-template-columns:260px minmax(0,1fr); gap:20px; }
main, .card { min-width:0; }
pre { max-width:100%; overflow-x:auto; -webkit-overflow-scrolling:touch; }
@media (max-width:880px) { .layout { grid-template-columns:1fr; } .toc { position:static; } }
@media (max-width:560px) {
  table, thead, tbody, tr, th, td { display:block; width:100%; }
  thead { display:none; }
}
```

## Komuna UI parity guard

When a prototype or approved reference specifies an interaction model, copy its semantics—not merely its visual theme. In particular, never call a static image grid a carousel. Before declaring parity, exercise the interaction and verify all expected entity states, including missing-image placeholders. For the Program/Product/Package-specific checklist, read `references/program-detail-carousel-and-placeholder-verification.md`.

## Publication Workflow

1. Save the canonical source plan under `.hermes/plans/` or `docs/`.
2. Save the styled HTML at `/home/ubuntu/projects/komuna/docs/<slug>.html`.
3. Publish with:

```bash
chmod 644 /home/ubuntu/projects/komuna/docs/<slug>.html
sudo ln -sfn /home/ubuntu/projects/komuna/docs/<slug>.html /usr/share/nginx/html/prds/<slug>.html
sudo nginx -t
```

4. Verify local and public:

```bash
curl -sI http://127.0.0.1/prd/<slug>.html
curl -sI https://komuna.ahsanworks.com/prd/<slug>.html
curl -sS 'https://komuna.ahsanworks.com/prd/<slug>.html?v=mobile-check' | grep -E 'viewport|@media|max-width'
```

5. If possible, run a browser/mobile viewport check at 390px width and inspect for horizontal overflow.

## Verification Checklist

- [ ] Public review page returns HTTP 200.
- [ ] HTML includes viewport meta tag.
- [ ] CSS includes mobile breakpoints for ≤880px and/or ≤560px.
- [ ] TOC/sidebar collapses on mobile.
- [ ] Tables or wide content do not force page-wide horizontal scrolling.
- [ ] Code blocks scroll independently if needed.
- [ ] Page uses Komuna theme tokens and visual style.
- [ ] Final response includes the public review link.

## Reference Notes

- `references/admin-sessions-design-artifact-correction.md` — correction pattern for Komuna dashboard design/plan artifacts: split text plan and visual design pages; dashboard design pages should show the full dashboard context, reuse actual component/class vocabulary, and place mobile below desktop on the same design page when requested.
- `references/admin-dashboard-hierarchy-deduplication.md` — use when repeated program/workspace identity and card-within-card framing make an admin feature page redundant; map global/program/feature levels, flatten decorative shells, and preserve interactive semantics.
- `references/admin-tab-visual-normalization-preserve-flows.md` — implementation handoff for aligning many admin tabs to one approved visual baseline: classify elements before removal, preserve every operational component/state, update only stale top-level-header assertions, and verify the safe Komuna build/deploy path.
- `references/manager-session-assignment-row-layout.md` — compact fix pattern for scoped manager session rows: fall back to occurrence DTO identity when the member lookup is intentionally absent, preserve role scoping, keep lock state inside the existing status cell, and regression-test the direct CSS Grid child count.
- `references/subscription-xendit-prd-mobile-fix.md` — concrete correction from the subscription/Xendit PRD: fix the published PRD page itself, not only the implementation-plan content; includes CSS and verification pattern.
- `references/subscription-package-entitlement-model.md` — domain model for subscription plans in Komuna review artifacts: packages are sellable bundles, subscription entries grant renewable entitlements, product scopes can be one-or-more products, and subscription bookings create `voucher_claims.subscription_id` claims rather than pre-generated vouchers.
- `references/wallet-voucher-pocket-animation-preview.md` — approved wallet voucher pocket preview/implementation pattern: preserve approved animation timing, animate the actual pocket stack out/back, allow overflow, avoid fake return voucher layers.
- `references/wallet-voucher-pocket-animation-preview.md` — preview-artifact pattern for wallet voucher pocket animation fixes: reuse live wallet component structure, demonstrate literal pull-out/empty-pocket/return sequencing, and avoid changing already-approved animation feel.
- `references/shared-footer-layout-implementation.md` — approved shared-footer implementation pattern: small user edits during implementation approval are in-scope; dashboard footer belongs in `DashboardShell` outside `.dashboard-content`; omit the “Explore” footer group when following this approved design.
- `references/footer-layout-design-preview.md` — footer design preview pattern: when footer work spans public Discovery-style pages and dashboard, publish a static approval page showing both public/editorial and compact dashboard footer variants before implementation.
- `references/hallmark-app-design-proposal.md` — broad Komuna app-design suggestion pattern: do a small read-only UI inspection, publish a responsive static proposal/mockup, preserve the real navigation model, and keep implementation gated.
- `references/public-discovery-landing-redesign-from-supplied-reference.md` — workflow for turning a supplied ZIP/demo into a compact, commercially persuasive Discovery prototype: inspect the real surface first, separate borrow/preserve/reject decisions, define measurable first-viewport acceptance, derive honest merchandising categories, refine existing topbar controls, and keep implementation gated.
- `references/public-program-detail-catalog-prototype.md` — prototype pattern for replacing the public Program Detail session-instance rail with real ProductCard and PackageCard visual patterns in adjacent below-hero sections, including fidelity, scope gating, responsive stacking, and screenshot verification.
- `references/static-prototype-css-integrity-and-stacked-merchandising.md` — landing/discovery prototype correction: replace rejected filter pills with database-backed stacked category sections, preserve the centered shell, and prevent `read_file` line prefixes or truncation markers from corrupting inline CSS during artifact rewrites.
- `references/discovery-hero-program-carousel-prototype.md` — minimal accessible autoplay carousel for the Discovery hero: use real program records, images, and detail routes; pause on hover, honor reduced motion, and verify every target publicly.
- `references/discovery-database-merchandising-implementation-plan.md` — agent-ready handoff from approved Discovery prototype to real database-backed, mutually exclusive Popular/New/Open sections; randomize Open once per reload, preserve real topbar routes, reuse app primitives, and regression-test unrelated pages.
- `references/discovery-mobile-desktop-card-scroll-rail.md` — mobile Discovery pattern that preserves the desktop card anatomy at a smaller size in native horizontal snap rails, with a semantic View all tile as the final rail item and no scroll-end JavaScript.
- `references/public-program-detail-catalog-implementation.md`
- `references/public-program-detail-catalog-implementation.md` — live React handoff after approval: reuse existing DTO data without duplicate/bogus fetches, remove dead session/voucher requests with removed workflows, preserve slug-first routes, eliminate inline-style card overrides, handle root-relative assets and failed media, and gate deployment on screenshot QA.

## Implementation Handoff: Privileged Leave Guards

When an approved Komuna plan prevents Admins or product Managers from leaving a program:
- Treat UI hiding as explanation only; the API is the security boundary.
- Enforce leave with an atomic conditional membership update, not a privilege check followed by an unconditional update.
- Recognize both manager representations (`program_member_roles` and `product_managers`) in authorization and normalize both into the program-detail DTO so the UI agrees with the backend.
- Replace Leave with concise role-aware copy such as “You’re a manager. Revoke your role to leave,” while retaining ordinary member actions.
- Regression-test ordinary members, Admins, role-row Managers, assignment-only Managers, dual representation deduplication, and combined Admin+Manager UI copy.
- Detailed implementation recipe: the `komuna-operations` support file `references/privileged-member-program-leave-guard.md`.

## Common Pitfalls

1. **Adding responsive requirements to the implementation plan instead of fixing the review page.** If the user says the public PRD is hard to read on mobile, update the HTML artifact itself.
2. **Desktop-only grid.** A sticky left TOC with a wide content column is fine on desktop but must collapse on mobile.
3. **Tables as tiny text.** Convert tables to block rows or scroll containers on phones.
4. **Forgetting cache busting.** Cloudflare may serve stale HTML. Verify with `?v=<label>` after updates.
5. **Changing product-plan content while fixing readability.** Keep content changes separate from artifact presentation fixes unless the user asked for both.
6. **Design artifact shell vs. real app shell mismatch.** Before implementing an approved layout element from a static mockup (especially footer/header/dashboard shell), audit the actual route/component tree for existing instances. Komuna dashboard pages may already render `<Footer />` inside page components while `DashboardShell` wraps them. Do not add another shell-level footer until you have searched for existing `<Footer />` usage and verified there will be exactly one rendered `contentinfo` landmark. CSS rules such as `.dashboard-content > footer:last-child { display:none }` may hide only direct-child footers and do not prevent nested/page-level footers from existing; prefer avoiding duplicate DOM over hiding one with CSS.
7. **Footer/layout regression tests that only check text.** When changing global layout landmarks, add a regression assertion for count/uniqueness (for example `getAllByRole('contentinfo')).toHaveLength(1)`) in addition to copy checks, and include a nested/page-footer fixture if the shell can wrap page content.
8. **Animation previews that fake or replace the approved product component.** When the user asks for a Komuna animation preview, reuse the relevant product component geometry/class names and demonstrate the exact object relationship they care about. For wallet voucher pockets, the visible vouchers inside the pocket must be the animated objects: open pulls the existing stack out and leaves the pocket empty; close uses the same stack path in reverse, never separate throwaway return elements. If the user approves the voucher modal and animation but asks to add session selection, preserve the voucher-ticket modal as the first stage—do not replace its `.wallet-ticket` children with session cards. Use the sequence **pocket → animated voucher modal → voucher Claim → separate sessions modal → booking confirmation**, with one active dialog/focus trap at a time and Back navigation that restores the prior stage without replaying entrance animation. Keep existing timing/easing exactly when the user says the animation is good. See `references/wallet-voucher-pocket-animation-preview.md`.
9. **Calling a screenshot “verified” while visible alignment defects remain.** After any composition change, inspect paired card rows, media top edges, actions, narrowed hero stats, and CTA wrapping. If the screenshot shows overlap or drift, patch and capture again before reporting success. For public Program Detail catalog and split-hero gallery work, follow `references/public-program-detail-catalog-prototype.md`.
10. **Correcting the card shell when the complaint is about card content.** When the user says card “alignment” or “justification,” inspect title, description, metadata, price, and action placement separately from outer card size and row geometry. If actions are requested on the right, give them a dedicated right-side column; do not merely bottom-align them below the information. Keep the information top-left aligned and stack multiple actions within the right-side action area.
11. **Creating blank space while moving actions right.** A dedicated action column does not require equalizing cards with `height:100%` or an arbitrary `min-height`. Let content/media determine height, then use the shared outer grid only to align paired rows. On mobile, prioritize compact media and reduced section spacing while preserving readable text and touch targets.
12. **Leaving prototype CTAs inert or semantically wrong.** Use the real Komuna public route shapes in interactive prototypes. Product details go to the Product page; session products link to Sessions with `?productId=` so filtering is automatic; Package purchase links go directly to checkout. Do not show Product cost when the approved design reserves pricing for Packages.
13. **Rewriting an artifact from display-oriented file output.** `read_file` prefixes lines with `LINE_NUM|` and may visually truncate long lines. Never write that rendered content back wholesale. It can persist `1|` text, inject truncation markers, and terminate inline CSS early—often leaving the header/hero styled while later grids/cards become plain text. Prefer targeted patches; then fetch the public HTML and assert no line prefixes/truncation markers and the presence of critical late CSS selectors before visual QA.
14. **Keeping filter pills after the user requests category sections.** Filtering controls and merchandising sections are different information architectures. When pills/tabs are rejected, show each category heading and its relevant database-backed programs simultaneously in vertically stacked sections. Preserve the approved centered max-width shell across the hero and every section; do not allow the card area to collapse into a narrow text column.
