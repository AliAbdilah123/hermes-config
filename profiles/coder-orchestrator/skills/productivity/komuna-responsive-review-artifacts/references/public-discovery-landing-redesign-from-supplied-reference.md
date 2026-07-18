# Public Discovery landing redesign from a supplied reference archive

Use this note when a user supplies a ZIP or standalone demo as a layout reference for redesigning Komuna's public Discovery/landing page and requires a prototype before implementation.

## Read-only discovery workflow

1. Extract and inspect the supplied archive as a **composition reference**, not as source code to merge.
2. Inspect the real Komuna surface before designing:
   - `apps/web/src/pages/DiscoveryPage.tsx`
   - `apps/web/src/components/layout/TopNav.tsx`
   - existing theme/language controls
   - `apps/web/src/components/discovery/ProgramGrid.tsx` and `ProgramCard.tsx`
   - `apps/web/src/globals.css`
   - Discovery tests and i18n keys
3. Record separately:
   - ideas to borrow from the reference;
   - real Komuna behavior and visual language to preserve;
   - demo-only behavior/data/dependencies to reject.
4. Publish two artifacts: a comprehensive plan and a separate interactive/static design prototype. Explicitly label the prototype as non-live.
5. Keep implementation gated until the user explicitly asks to implement and deploy.

## Borrow vs. preserve

Good ideas to borrow from a compact commercial reference:
- a shorter campaign hero;
- visible merchandising/category controls;
- denser cards and clearer hierarchy;
- recognizable icon-led theme/language controls;
- commercial framing that helps guests compare choices quickly.

Preserve from the real product:
- Komuna paper/ink/terracotta tokens and batik character;
- actual topbar, auth, routes, footer, theme persistence, and i18n;
- real `ProgramCard` data and image fallbacks;
- accessibility, reduced motion, loading/error/retry states;
- truthful membership visibility, member count, rating, and pricing.

Reject from a standalone demo unless explicitly requested:
- fake booking/dashboard/voucher state;
- hard-coded sample programs as production data;
- scaffolding, CDN scripts, or new dependencies;
- duplicate search or card systems when Komuna already has them.

## First-viewport acceptance

When the complaint is that the hero consumes too much space, make the requirement measurable rather than saying only “make it compact.” At common desktop/laptop sizes such as 1440×900 and 1280×720, aim to show:

- the complete topbar;
- the complete compact hero;
- category/section controls;
- at least the top of the first program row.

A practical desktop hero target is roughly 300–360px, but the visual acceptance outcome matters more than a fixed number. Verify tablet and 390px mobile layouts separately and check for horizontal overflow.

## Honest merchandising categories

Never invent commercial labels from sample-array position. Derive categories from real fields or documented backend semantics:

- **Most Popular:** member count descending, then rating, or an authoritative featured/popularity rank.
- **New Programs:** creation timestamp descending.
- **Open to Join:** public first, then approval-based; keep private/invitation-only out unless policy says otherwise.
- **Free Trial:** use only when real free-trial or zero-price semantics exist.

If the landing endpoint returns too few or arbitrarily ranked records, verify its semantics before sorting client-side. Prefer an existing listing sort/filter parameter; propose the smallest API enhancement only if needed, with no speculative schema.

## Compact interaction model

For a space-constrained landing page, prefer segmented tabs that replace one program rail/grid over stacking several near-duplicate sections. This keeps the first page commercially scannable and avoids duplicate cards. Keep the full search experience on the dedicated `/programs` route unless the user explicitly wants landing-page search.

## Topbar control fidelity

A reference may suggest a better visual treatment without changing behavior:

- reuse the real theme provider and persistence;
- use one clear sun/moon icon button or an equally compact accessible group;
- use a globe-led ID/EN control or disclosure while preserving i18next;
- retain keyboard focus, accurate accessible labels/state, and comfortable touch targets;
- do not alter auth, dashboard visibility, notifications, or profile behavior while polishing controls.

## Prototype QA

Before reporting the review artifact complete:

- exercise category switching, theme, and language demonstrations;
- verify responsive metadata and breakpoints;
- check desktop and mobile composition visually when browser tooling is available;
- verify both plan and design URLs return HTTP 200 with cache-busting queries;
- state clearly that application code and the live route remain unchanged.
