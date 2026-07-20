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

## Verification discipline

- Run targeted lint on changed files as the feature gate.
- Run repository-wide lint too, but clearly separate pre-existing unrelated failures from changed-file failures. Do not silently fix unrelated code.
- Run feature tests and the production build independently so one pre-existing failure does not prevent collecting other evidence.
- A screenshot taken immediately may capture a loading state. Verify the API, then allow enough browser virtual time for the application and request to settle before judging data-backed geometry.
- At the named acceptance viewport, visually prove the requested content is fully visible, media/fallbacks load, spacing is comfortable, and no overlap or page-level overflow exists.
- Exercise the primary interaction path, dismissal paths, keyboard behavior, focus return, theme variants, and console output.
- Verify deployed asset timestamps/hashes and the cache-busted public URL.

## Pitfalls

- Calling a loading-state screenshot evidence that cards are missing.
- Reporting first-viewport success without a settled screenshot.
- Letting pills and the fixed Filter button share one overflow container.
- Copying unsupported prototype facets into production as disabled or misleading controls.
- Claiming “all tests pass” when unrelated repository tests or lint fail; report exact commands and boundaries.
- Allowing an agent to deploy/commit without independently checking HEAD equals upstream and the public route serves the new build.

See `references/data-backed-mobile-search-verification.md` for a concrete verification recipe.
