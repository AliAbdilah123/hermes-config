# Data-backed program-detail production parity

Use this checklist when an approved static Program Detail prototype becomes a real responsive page.

## Data and routing

- Build program, product, package, session, pricing, status, and carousel content from existing API responses.
- A prototype may contain filler records to demonstrate a row; production must not.
- Preserve active/archive filtering, slug-first routes, currency formatting, auth, membership, and role/leave guards.
- Whole-card package/product navigation must not contain nested links or buttons.

## Responsive geometry

- Desktop catalog requirement such as “four per row” means a four-column grid; fewer real records leave unused columns rather than inventing or stretching data.
- If mobile cards must be 50% shorter, define and test a concrete height range. Preserve price and action; clamp secondary copy first.
- Increasing all small typography can break fixed-height cards. Reallocate media/body rows before raising font sizes.
- Keep media taller than body only where requested; on highly compact mobile cards, prioritize legibility and explicit acceptance targets.

## Tabs

- Use tablist/tab/tabpanel semantics, roving tabindex, ArrowLeft/Right/Home/End, and hash deep links.
- Scroll the active tab fully into view after initial render and whenever the hash changes, without stealing focus.
- A clipped neighboring tab can intentionally advertise horizontal scrolling. Confirm `documentElement.scrollWidth <= clientWidth`; do not call this page overflow solely from a screenshot.

## Carousel

- Derive slides from already-fetched real data; missing images remain typed placeholder slides.
- Support previous/next, dots, counter, reduced motion, pause on hover/focus/hidden document, and timer reset after manual navigation.
- At mobile breakpoints, reserve distinct regions for stage, caption, and metadata. Check placeholder labels, caption text, dots, and counter for overlap.

## Sessions and booking

- Fetch the requested bounded count (for example five), then defensively slice.
- Compact mobile rows should have stable height; clamp long product/title text rather than allowing row growth.
- Keep real booked/full/sign-in/book behavior and minimum touch size.
- Redesign shared booking modals without replacing voucher eligibility, FIFO selection, no-voucher package routing, focus trap, Escape, focus restoration, success, and error behavior. Regression-test other modal consumers.

## Evidence sequence

1. Changed-file lint.
2. Focused feature and shared-consumer regression tests.
3. Production build.
4. Full lint/test only as a separate baseline signal; report unrelated failures explicitly.
5. Start the real API and frontend with the project’s effective environment precedence. Verify the proxied API URL before screenshots.
6. Capture settled desktop and named mobile viewport states for every tab and modal state.
7. Inspect visuals and console/network output; distinguish intentional component scrolling from page-level overflow.
8. Deploy through the real production path, verify cache-busted public assets/page, then commit and push only task files.
