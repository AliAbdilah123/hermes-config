# Exact design artifact → data-backed frontend

Use when an HTML/CSS prototype or design artifact is the approved visual contract for a real application.

## Fidelity contract

Do not reduce the artifact to a feature list and then produce a generic UI. Inventory every visible surface before implementation:

| Surface | Required evidence |
|---|---|
| Auth | rendered login state |
| Shared shell | sidebar/topbar/mobile navigation |
| Overview | hero, metrics, assigned content, activity, secondary panels |
| Catalog/list | filters, cards, badges, actions |
| Admin/member surfaces | tables, forms, invites, decisions |
| Detail/lesson | focused workspace, progress, completion state |
| Responsive variants | desktop and named mobile viewport |

For each surface, preserve composition, hierarchy, density, typography, spacing, colors, radii, shadows, and responsive behavior—not merely labels and routes. A small shell plus generic cards is not a faithful implementation even if all workflows function.

## Bind design to real data

- Preserve the design composition using persisted API data.
- Omit unsupported prototype-only controls rather than presenting fake behavior.
- Do not substitute arbitrary metrics or filler records to make the screenshot look populated.
- Wait for every API-backed region used in visual acceptance before capturing screenshots. A screenshot taken after only the page heading appears can falsely show missing cards or empty regions.
- Verify card/detail actions use the domain entity required by the target API. Do not assume a package ID is also a lesson ID; exercise the rendered card-to-detail flow publicly.

## Preview-first correction loop

1. Keep production unchanged and publish an isolated authenticated preview.
2. Run a surface-matrix review against the source artifact before sharing.
3. Capture settled viewport screenshots at desktop and mobile.
4. Exercise at least one real navigation/mutation path on both viewports.
5. Measure document overflow and fixed/sticky geometry.
6. Share preview only after blocking fidelity defects are resolved.
7. Promote only after explicit approval.

## Screenshot interpretation

Full-page screenshots can composite `position: fixed` mobile navigation at an apparent mid-document location. Before calling this an overlap defect, measure its bounding rectangle in a normal viewport and require:

- `nav.bottom == innerHeight` (within rounding tolerance);
- content bottom padding reserves the nav height plus safe area;
- `documentElement.scrollWidth <= clientWidth`;
- a viewport screenshot confirms the visible state.

Treat a wrapped primary mobile CTA as a polish failure when the source design shows one line. Prefer modest scoped padding/font/`white-space` correction; do not redesign the action row.

## Release gate

Functional tests and successful builds are necessary but not sufficient. Do not report READY when the design artifact and deployed screenshots materially differ. Report separately: functional parity, visual fidelity, preview publication, approval, production promotion, and public E2E.
