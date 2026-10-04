# Full-product UI revamp gates

Use when an approved visual direction must replace an authenticated product UI across multiple routes and states.

## Before implementation

Define a route/surface matrix with, for each entry: exact URL/state, renderer, shell variant, retained behavior, responsive contract, and test/browser evidence. Include list/detail pairs, early-return routes, overlays, auth/invitation, notifications/account, loading/error/empty states, and distinct inspector versus full-page detail experiences.

Define “material migration” concretely before delegating or reviewing. Require explicit component markup or owned selectors for each named surface; adding only a wrapper class and a final global recoloring block does not qualify. State which legacy declarations must be removed or scoped.

## Implementation order

1. Shared tokens and primitives.
2. Shell and exact-route navigation.
3. List/detail and history restoration semantics.
4. Feature surfaces and overlays.
5. Auth, invitations, notifications, account controls, and feedback states.
6. Responsive/accessibility behavior.
7. Tests, browser proof, independent review, then release.

Do not let shell navigation treat a top-level section as identical to every detail route in that section. Clicking Projects from project detail must reach the Projects list. Separate `activeSection` from `currentExactDestination`.

Make asynchronous navigation transactional. Load required destination data before committing rendered route state. For `popstate` failure, either render a coherent destination error surface or restore the last successfully rendered URL; never leave the failed URL paired with the previous screen.

Every authenticated route—including early-return job and conversation routes—must use the intended shell contract: global navigation, breadcrumb/top bar, notifications, and actionable account/profile/logout controls. A shell wrapper with plain email is incomplete.

For accessible mobile navigation, prefer the existing modal/dialog primitive for focus containment, inert background, Escape/backdrop dismissal, scroll locking, and opener-focus restoration. Ensure exactly one accessible close control.

## Fail-closed review

Run review against the route/surface matrix, not a vague impression. Require findings to name a file/location, observable defect, and violated acceptance item. Separate:

- blocking correctness/accessibility/spec defects;
- browser-verifiable visual concerns;
- optional polish.

A passing test/build is necessary but not sufficient. Conversely, do not repeatedly reject on undefined “not material enough” grounds: the matrix and per-surface acceptance criteria must make that judgment deterministic.

After each corrective pass, independently rerun tests, build, and diff checks from the final workspace. Then request a fresh reviewer who reads prior findings and explicitly marks each blocker fixed or still reproducible.

## Minimum regression evidence

- detail-to-list navigation through the rendered application;
- successful and failed Back/Forward restoration with URL/UI coherence;
- shell controls present on ordinary, job, and conversation routes;
- drawer close uniqueness, focus containment, Escape/backdrop behavior, navigation closure, scroll lock, and focus restoration;
- representative rendering/interactions for board, workspace, project, inspector, full-page job, conversation, dialog, notification/account, auth/invitation, status badges, and loading/error/empty states;
- scoped CSS with superseded global header/nav/palette declarations removed or narrowed;
- required viewport screenshots, document-overflow measurements, console/network checks, and authenticated exact-route E2E.

## Release gate

Do not commit, push, or deploy while independent review is failing. After review passes: commit and push the exact verified tree, deploy that committed revision, and run authenticated public desktop/mobile E2E. Report implementation, review, deployment, and public E2E as separate evidence boundaries.
