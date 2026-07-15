# Hallmark app design proposal pattern

Use this when the user asks for a better Komuna app design, design direction, “hallmark” app design, or high-level UI/UX recommendation without explicit implementation permission.

## Session-derived pattern

- Treat the request as a review artifact/design proposal, not a live app change.
- Do a small read-only inspection of current UI structure first so the proposal does not invent false navigation. In the observed Komuna app:
  - public discovery uses warm paper/ink/accent tokens, serif headings, batik-inspired hero texture, sticky top nav, and featured programs;
  - admin program pages use the horizontal `ProgramDetailLayout` tab shell, not a sidebar;
  - admin dashboard uses stat cards, nav tiles, and program-scoped routes under `/dashboard/programs/:id/*`.
- Create a styled, responsive HTML artifact with a concise product-design direction and a static visual mockup.
- Include a visible implementation gate: design suggestion only; no live app behavior changes until explicit approval/implementation request.
- Verify local and public PRD routes with cache-busting where possible.

## Useful design framing

“Hallmark Community OS” worked as a class-level direction for Komuna:

1. Discovery-first public surface — editorial program cards, trust cues, category/search, package/session previews.
2. Member home — upcoming sessions, wallet/vouchers, purchases, notifications, and next useful action.
3. Operator cockpit — today/session activation, attendance, QR/check-in, booking approvals, support issues.
4. Admin command center — program health, products/packages/purchases/vouchers/sessions in the existing tab shell.
5. Design-system cleanup — consistent cards, pills, tabs, filters, responsive data lists, empty states, and mobile stacks.

## Pitfalls

- Do not turn a broad design suggestion into implementation.
- Do not invent a sidebar for admin pages when the current app uses horizontal tabs.
- Do not produce prose only; this user expects a public styled HTML artifact for review.
- Do not skip current-source inspection; even a small read-only pass prevents false UI structure.
