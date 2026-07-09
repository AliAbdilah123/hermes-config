# UI redesign review artifacts: plan/design separation and theme fidelity

Use this reference when a user asks for a UI redesign plan or static review artifact.

## Lessons from admin dashboard sessions redesign

A user correction exposed three durable pitfalls:

1. **Do not combine implementation plan and visual design in one crowded page.**
   - Publish a plan page for scope/tasks/tests/risks.
   - Publish a separate design page for the visual mockup and interaction states.
   - Cross-link both pages clearly.

2. **Do not invent missing layout structure.**
   - Inspect the actual host page layout first.
   - If the current page has tabs and no sidebar, the mockup must show tabs and no sidebar.
   - For dashboard/admin pages, inspect layout components such as tab shells, headers, route layouts, and CSS before drawing the mockup.

3. **Use the product’s real theme, not a generic review-doc theme.**
   - Pull actual tokens from app CSS where possible (`--paper-*`, `--ink-*`, `--accent-*`, font variables, radii, borders, max widths).
   - For Komuna specifically, copy the real tokens from `apps/web/src/globals.css` and the local inline helpers from the target page (`cardStyle`, `buttonStyle`, `inputStyle`, `sectionLabel`) before drawing the design.
   - If the app uses a page shell or tab component, mirror its spacing and visual rhythm.
   - The design artifact should look like a static screenshot of the future product page, not like the implementation-plan document.
   - If the artifact mostly looks like a styled PRD/document page with a mockup inside it, it fails this checklist; rebuild it as the actual page surface first, then add a small review note outside the mockup.

## Required workflow

1. Inspect the current page/component and its CSS/theme tokens.
2. Identify real navigation/page structure: tabs, topbar, sidebar, centered content shell, route layout, etc.
3. Create two artifacts when both planning and design are needed:
   - `<slug>-plan.html`: tasks, paths, tests, risks, implementation gate.
   - `<slug>-design.html`: visual mockup only, with actual app theme/layout.
4. Cross-link both pages.
5. Verify the design artifact contains visible evidence of the real structure (e.g. active tab labels) and theme tokens/classes.
6. If the user corrects the artifact, update both the source plan and the relevant public HTML before replying.
7. When a user approves a previous visual direction but adds/changes requirements, do **not** redesign the mockup unless the requirement directly changes visual layout. Preserve the approved design and make the smallest update: plan/spec text first, then only labels/notes/disabled states in the design artifact. Never replace a liked design while incorporating spec decisions.

## Acceptance checklist

- [ ] Plan and design are separate when visual approval is requested.
- [ ] Design page uses real app navigation structure.
- [ ] Design page uses real theme tokens or faithful copied CSS values.
- [ ] Design page has enough product-native visual character to feel like the app, not a sterile wireframe: reuse existing accent treatments, subtle textures/patterns, status colors, stats/card rhythm, and empty/disabled states from the product. "Theme-correct but bland" is still a failed design artifact.
- [ ] No fake sidebar/topbar/tab pattern is introduced.
- [ ] Manual/product-specific corrections are reflected in both plan and design where relevant.
- [ ] When the user adds a requirement after seeing the plan/design, explicitly update the spec wording in both source markdown and public HTML; do not leave it implied by implementation tasks only.
