# Visual Reference Fidelity for SaaS Dashboards

Use when a user supplies a screenshot/reference and later says the app does not look like it yet.

## Lesson

A successful build is not enough. The deliverable is visual similarity to the reference, verified against a rendered screenshot. If the existing product UI is structurally different, do a targeted fidelity pass rather than incremental polish.

## Fidelity Pass Checklist

1. Re-open/analyze the reference image into concrete UI elements:
   - shell/sidebar shape, width, colors, active nav state
   - top bar content, profile/notification/city controls
   - KPI card count/order/labels
   - main grid proportions and panel placement
   - table/list row density, badges, buttons, chart/progress elements
   - exact content density and mock data needs
2. Make the first visible route match the reference state.
   - If login blocks the reference-like dashboard, either auto-auth the demo route or make the screenshot-style dashboard visible by default for the prototype.
   - Preserve backend auth where needed, but do not let auth UX prevent visual review when the user asked for design matching.
3. Seed or hardcode realistic demo/mock data so empty states do not destroy the visual match.
   - For BI dashboards, populate KPI cards, opportunity rows, inbox rows, challenge/progress lists, summary tables, and CTA cards.
4. Rebuild and deploy the actual served app, not only source files.
5. Capture a headless/browser screenshot of the deployed route and compare it visually with the reference.
6. Report the visual check and any caveat honestly.

## Pitfalls

- Do not interpret "build the design system first" as permission to ship a generic design system that only loosely follows the screenshot.
- Do not stop at CSS token changes if the layout hierarchy is wrong; match the screenshot's component inventory and grid.
- Do not leave a login screen as the first rendered page when the supplied reference is an authenticated dashboard and the user is judging visual similarity.
- Do not rely on sparse real database rows; mock/seed data is often required for a dashboard screenshot to look right.
