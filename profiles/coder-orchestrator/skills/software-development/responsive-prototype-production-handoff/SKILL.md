---
name: responsive-prototype-production-handoff
description: Implement an approved responsive UI prototype in an existing application while preserving interaction semantics, scoping regressions, and proving live viewport behavior.
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [responsive-ui, prototype, implementation, browser-qa, tdd]
---

# Responsive Prototype → Production Handoff

Use when a user approves a static or interactive responsive prototype and explicitly requests implementation in the real application.

## Core workflow

1. Read the approved prototype, implementation plan, real page/component tree, shared styles, data helpers, translations, and nearby tests.
2. Treat the prototype as the visual and interaction contract, not source code to paste into production.
3. Preserve the real application’s data flow, routes, shared components, accessibility primitives, themes, and desktop/tablet behavior.
4. Apply only the user’s requested refinement to the approved baseline. If they ask for “a little breathing room,” increase gaps/padding modestly while retaining measurable first-viewport requirements.
5. Use strict TDD for behavior changes: add focused failing tests, observe the expected failures, implement minimally, then rerun targeted and regression tests.
6. Scope responsive overrides under the page root. Never globally rewrite a shared card/grid to satisfy one mobile page.
7. Build and deploy using the project’s actual production path, then verify the public route with cache busting.
8. Commit and push only task-related files; leave unrelated untracked plans, uploads, databases, and artifacts untouched.

## Filter-sheet pattern

For a mobile quick-filter rail plus bottom sheet:

- Put only quick pills in the horizontally scrolling region; keep the 44px Filter trigger in a fixed trailing column.
- Derive quick options from real helpers/data rather than hard-coding prototype labels.
- Copy committed filters into draft state when opening.
- Apply commits atomically. Cancel, close, backdrop, and Escape discard the draft.
- Restore trigger focus, trap focus, lock/restore body scroll, respect safe-area insets, and disable transition motion for reduced-motion users.
- Implement only filters supported by current contracts. Omit prototype-only fields rather than presenting fake functional controls.

## Production parity and responsive acceptance

- Bind production cards, counts, prices, routes, sessions, and carousel slides exclusively to real application data. Never add filler records merely to complete a prototype grid row.
- Preserve approved design outside the user's named deltas. Scope post-approval iterations to the requested component and viewport instead of rebalancing areas that already passed.
- Turn vague responsive deltas into measurable targets before delegation (for example, “50% shorter” becomes a bounded mobile card-height target), then verify actual pixels at the named viewport.
- A horizontally scrollable tablist may expose part of the next tab as an overflow affordance, but the active tab must scroll fully into view on initial mount/deep-link changes as well as after clicks. Distinguish intentional tab-strip overflow from page-level overflow.
- Larger typography plus fixed-height cards requires budgeting body space first: rebalance media/body rows, clamp secondary descriptions, and keep prices/actions visible. Never let a fixed CTA overlap copy.
- On mobile carousels, give captions, counters, dots, and placeholder labels separate geometry; desktop overlays commonly collide at narrow widths despite no page overflow.
- When absolutely positioned carousel stage, slide, and link share a grouped selector, apply footer reservation (`bottom`) only to the outer stage. Repeating it on nested absolute layers compounds the inset and creates a false empty block. See `references/mobile-carousel-absolute-inset-compounding.md`.
- For reported spacing/alignment defects, compare both outer bounds and nested padding. A hero and tab panel can share the same width while the tab scroller's extra padding makes their visual indentation differ. Normalize one mobile outer gutter before changing component sizes.
- Compact mobile session rows need stable anatomy: bound row height, clamp long titles, preserve booking state/action size, and prevent content length from changing the silhouette.
- When the user asks for cards to load vertically or reports horizontal card scrolling, fix the sibling-list axis first. Preserve each card’s approved internal anatomy unless they explicitly request a card redesign. Inspect shared rail rules for fixed flex-basis, overflow, snap behavior, and `!important`, then apply the smallest page-scoped mobile override.

See `references/mobile-list-axis-vs-card-anatomy.md` for the parent-list vs. card-anatomy diagnostic, minimal scoped CSS pattern, and rendered-geometry verification.
See `references/mobile-section-document-reordering.md` when a desktop-owned section must move below tabs or to another semantic DOM position only on mobile.
See `references/program-detail-production-parity.md` for a concrete data-backed responsive handoff checklist.

## Verification discipline

- When introducing a global React context into previously standalone public components, preserve isolated rendering: either give the context a safe production default (for example, the existing default language with a no-op setter) or update every component test/story host to use the provider. Run existing direct-render tests, not only new provider-aware tests; otherwise the app root can work while reusable components and legal-page tests break.
- Invoke focused Vitest files through the package executor (for example, `pnpm --filter frontend exec vitest run path/a.test.tsx path/b.test.tsx`). Do not append file arguments after an extra `--` to a package script unless that script is known to forward them correctly; it may run the whole suite and obscure feature regressions with unrelated failures.
- After any final repair—even a small compatibility fix—rerun the requested root production build and treat that newest run as the verification evidence before reporting completion.
- Run targeted lint on changed files as the feature gate.
- Run repository-wide lint too, but clearly separate pre-existing unrelated failures from changed-file failures. Do not silently fix unrelated code.
- Run feature tests and the production build independently so one pre-existing failure does not prevent collecting other evidence.
- A screenshot taken immediately may capture a loading state. Verify the API, then allow enough browser virtual time for the application and request to settle before judging data-backed geometry.
- At the named acceptance viewport, visually prove the requested content is fully visible, media/fallbacks load, spacing is comfortable, and no overlap or page-level overflow exists.
- Exercise the primary interaction path, dismissal paths, keyboard behavior, focus return, theme variants, and console output.
- Verify deployed asset timestamps/hashes and the cache-busted public URL.

## Approved-prototype recovery and production-contract reconciliation

- Before asking the user to restate or reapprove a prototype, search conversation history and inspect existing prototype routes/files. Treat the latest approved revision and its follow-up changes as the visual contract; do not recreate an artifact that already exists.
- Translate prototype-only choices onto real domain rules instead of copying illustrative behavior literally. For example, when production booking selects vouchers FIFO, present a selectable entitlement summary and let the existing booking flow choose the voucher; never invent voucher-selection APIs or fake records to mimic the mockup.
- Preserve unrelated dirty work in shared repositories. Stage, commit, and push only the feature files, then confirm the resulting commit contains the intended new files and excludes pre-existing modifications.
- A scoped commit does not make a build from a dirty workspace scoped: Vite/React and similar builds compile every working-tree modification. Before deploying, build from a clean worktree or temporary checkout at the committed SHA, then deploy that artifact. See `references/clean-artifact-deployment-from-dirty-worktrees.md`.
- Treat a clean-SHA build failure as a hard deployment gate, even when the dirty workspace builds. The dirty build may silently include unrelated uncommitted code or styles. Determine whether the feature truly depends on prerequisite dirty changes; commit only the minimal related prerequisites with focused verification, or revise the feature to build from HEAD. Never fall back to deploying, copying, or `rsync`ing the dirty-workspace artifact merely because targeted tests and a dirty-tree build passed.
- Enforce the gate operationally: run the clean-SHA build before any deployment command. If it fails, do not use a previously generated `dist/`, even if its feature tests passed and its bundle contains expected markers. Leave production unchanged and report exactly: committed/pushed, deployment blocked by clean-build failures. “Live HTTP 200” proves only that the old or dirty artifact is reachable; it is not evidence that the committed feature was deployed.
- When adding a mobile-only replacement component, do not remove the existing desktop control merely because the new component is hidden above a breakpoint. Render the original desktop component in a desktop-only wrapper and the new component in a mobile-only wrapper unless the task explicitly replaces both. Add an automated assertion that both viewport variants remain present and functional.
- If a delegated coding CLI has already written a substantial diff but stalls during verification, stop it after a reasonable bound, inspect the actual workspace diff, and run targeted tests, changed-file lint, build, commit, deployment, and route verification directly. The deliverable is the verified workspace result, not the delegate's final narration.
- When repository-wide lint fails, run changed-file lint separately and report both boundaries precisely. Do not fix unrelated lint debt as part of a focused responsive handoff.

## Pitfalls

- Asking for audience, action, tone, or approval again when the approved prototype and its latest revision can be recovered from history or the repository.
- Calling a loading-state screenshot evidence that cards are missing.
- Reporting first-viewport success without a settled screenshot.
- Declaring a responsive defect fixed from CSS declarations or nominally equal widths alone. Reproduce the user’s exact viewport/theme/data state and compare rendered outer edges, gaps, borders, controls, and overflow in pixels before deploying.
- Treating a technically non-overlapping carousel as visually acceptable. Mobile carousel acceptance includes composition: intentional crop, caption size/placement, arrow clearance from text, complete counter/dots, and no unexplained media-colored void. A labeled missing-image placeholder validates fallback geometry but does not prove real-image cropping; inspect a real-image slide separately when available.
- Misreading “same container” as “visually attached.” Shared centered width and vertical separation are independent requirements: use one shell primitive for horizontal geometry, then give the hero a complete bottom radius/border and an explicit gap before the tab bar.
- Repeatedly shipping incremental responsive guesses after the user reports the same visual defect. After one rejected fix, stop patching symptoms: restate the visual contract from the screenshot, use the exact requested delegation configuration when asked, independently inspect its diff, and withhold deployment until screenshot QA passes the named defects.
- Confusing list axis with card anatomy. “Cards listed vertically, not horizontally” means sibling cards must form a full-width column without list-level sideways scrolling; it does not mean stacking the image, body, and action inside each card. Revert rejected anatomy changes before fixing the parent list. Inspect high-specificity shared rules—especially `!important` rail rules—that can override an inline column declaration, then verify sibling positions and `scrollWidth <= clientWidth` at the named mobile viewport.
- Treating CSS-source assertions as visual proof. For creative prototypes, prefer viewport screenshot or DOM-geometry QA after the correction. If browser QA is unavailable, use a temporary `/tmp/hermes-verify-*` structural probe and explicitly label it ad-hoc verification rather than suite green.
- Letting pills and the fixed Filter button share one overflow container.
- Copying unsupported prototype facets into production as disabled or misleading controls.
- Claiming “all tests pass” when unrelated repository tests or lint fail; report exact commands and boundaries.
- Allowing an agent to deploy/commit without independently checking HEAD equals upstream and the public route serves the new build.

See `references/data-backed-mobile-search-verification.md` for a concrete verification recipe.
See `references/program-detail-tabbed-catalog-handoff.md` for tabbed catalog semantics, carousel/mobile-row geometry, deterministic active-tab alignment, and production-bundle QA.
See `references/desktop-session-calendar-detail-panel-handoff.md` for replacing a desktop upcoming-session rail with an initially empty selected-session details panel while preserving a separate mobile implementation.
