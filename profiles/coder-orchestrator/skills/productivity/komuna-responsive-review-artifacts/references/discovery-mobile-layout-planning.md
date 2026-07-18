# Discovery mobile layout planning from live code inspection

Use this reference when Komuna's public Discovery page is described as untidy or desktop-like on phones and the user requests an implementation plan before live changes.

## Inspect before proposing

Read these existing surfaces first:

- `apps/web/src/pages/DiscoveryPage.tsx`
- `apps/web/src/components/discovery/ProgramGrid.tsx`
- `apps/web/src/components/discovery/ProgramCard.tsx`
- `apps/web/src/components/discovery/DiscoveryHeroCarousel.tsx`
- the Discovery section and shared mobile-card rules in `apps/web/src/globals.css`
- `apps/web/src/__tests__/DiscoveryPage.test.tsx`
- `apps/web/src/components/discovery/__tests__/DiscoveryHeroCarousel.test.tsx`

Separate the user's symptom ("not neat") from code evidence. Typical evidence includes a single coarse mobile breakpoint, desktop-sized typography/padding carried into mobile, horizontal section headers that compete for width, fixed carousel heights, and inline grid declarations that force `!important` overrides.

## Minimum implementation path

1. Preserve `DiscoveryPage`, `TopNav`, `Footer`, `DiscoveryHeroCarousel`, `ProgramGrid`, and `ProgramCard` behavior.
2. Prefer Discovery-scoped CSS under `.discovery-page` / `.discovery-category`.
3. Remove only inline declarations that prevent responsive CSS—for example, move `ProgramGrid` column definitions to `.program-grid` rather than rewriting the component.
4. Add JSX only for stable semantic class hooks when existing selectors cannot safely target a region.
5. Do not change API data, merchandising selection, routes, auth visibility, i18n, theme persistence, carousel timing, or footer behavior during a layout-only fix.
6. Audit shared mobile `.program-card` rules: Discovery improvements must not regress Search Programs, Program Detail, or other surfaces using the same component.

## Concrete viewport strategy

Use named behavior ranges rather than a generic "make responsive" instruction:

- `>1024px`: preserve approved desktop composition.
- `761–1024px`: reduce spacing and use a two-column program grid; retain split hero only where it fits.
- `481–760px`: single-column hero, stable 16:9-ish carousel, wrapped/stacked category headers, single-column compact cards.
- `≤480px`: approximately 16px gutters, fluid headings, full-width primary CTA, compact supporting sections.

Validate 320, 360, 390, 430, 768, 1024, and 1440px, plus a phone landscape viewport.

## Mobile composition acceptance

- Hero copy is compact and remains dominant without consuming the whole first viewport.
- Primary CTA is obvious and touch-friendly; trust/supporting copy wraps beneath it.
- Carousel captions and dots never overlap; dots retain at least 40px targets and keyboard focus.
- Category title, description, and “View all” never collide.
- Cards preserve essential identity: image/fallback, title, location/member count, and price. Long names and locations clamp or wrap deliberately.
- How It Works uses compact stacked rows instead of oversized desktop cards.
- Clarity and FAQ use consistent mobile gutters; FAQ summaries target 44px height.
- No page-level horizontal overflow from 320px upward.

## Regression matrix

Check both light/dark themes and English/Indonesian text. Exercise loading, API error/retry, empty data, missing images, one carousel slide, and multiple slides. Confirm real `/programs` and program-detail routes, unchanged TopNav behavior, one `contentinfo` footer, no console errors, targeted tests, lint, and build.

## Review artifacts and gate

For plan-only requests, publish two separate responsive pages:

- comprehensive implementation plan;
- static 390px-style mobile composition preview.

Cross-link them, label the preview as non-live, include theme toggles, verify both local and public HTTP 200 with cache-busting, and state that approval is not implementation permission unless the user explicitly asks to implement/deploy.
