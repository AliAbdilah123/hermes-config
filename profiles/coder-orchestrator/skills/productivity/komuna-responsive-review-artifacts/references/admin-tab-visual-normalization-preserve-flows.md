# Admin Tab Visual Normalization While Preserving Flows

Use this implementation pattern when multiple admin tabs need to adopt one approved visual baseline without risking their operational workflows.

## Scope boundary

Treat the work as **header and geometry normalization**, not component redesign:

- Keep the shared dashboard shell as the sole owner of program/workspace identity.
- Give each tab one section-focused `h1`.
- Remove only duplicated identity, decorative eyebrows, release commentary, and outer presentation-only framing.
- Preserve every functional component: forms, filters, tables, charts, statistics, dialogs, status pills, actions, API calls, and loading/error/empty states.
- Keep meaningful internal section labels even if they use a different hierarchy treatment; do not remove them merely because top-level decorative labels are being removed.

Before deleting any element, classify it as one of:

1. **Shared identity** — belongs in the shell; remove tab-local duplicate.
2. **Section identity** — keep once as the tab `h1`.
3. **Operational content/control** — always preserve unless explicitly redesigned.
4. **Presentation-only duplication** — safe removal candidate.

## Minimal implementation path

1. Add a focused source/DOM regression check for one section `h1`, no top-level decorative eyebrow, and the approved shared width.
2. Move width and responsive padding into the existing shared layout CSS.
3. Remove conflicting page-local width/padding declarations and `!important` overrides.
4. Change only top-level header markup/copy in each tab.
5. Leave the approved baseline tab untouched.
6. Update old tests that intentionally asserted removed labels, but do not weaken functional-flow assertions.

## Test and build pitfalls

- Existing page tests may assert obsolete eyebrow text or a repeated program name as the tab heading. Replace those assertions with accessible section-heading assertions such as `getByRole('heading', { level: 1, name: 'Products' })`.
- Do not change assertions for meaningful nested analytics/report section labels when only top-level decoration is being normalized.
- A source-inspection Vitest test that imports `node:fs`, `node:path`, or uses `process.cwd()` requires Node types in the TypeScript config used by the production build. If `@types/node` is already installed, add `"node"` to `compilerOptions.types`; do not add another dependency.
- Broad suites can contain unrelated stale async fixtures. Prove the touched surface with focused functional page suites plus the consistency regression, and report unrelated failures honestly rather than changing product behavior to satisfy them.

## Deployment verification

For Komuna Vite builds:

- Build with `VITE_NEON_AUTH_URL` absent.
- Deploy the fresh `dist/` to the actual nginx root.
- Verify the public index references the new asset hash.
- Verify the bundle contains the local email-auth marker and no `neon.tech` marker.
- Confirm an admin nested route returns HTTP 200.

## Acceptance checks

- Program identity appears only in the shared shell.
- Every tab has one meaningful top-level heading.
- Approved baseline typography, width, and spacing are shared.
- No operational component or state was removed.
- Focused workflow tests and production build pass.
