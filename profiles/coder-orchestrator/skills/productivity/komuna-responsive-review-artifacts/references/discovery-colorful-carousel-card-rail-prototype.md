# Discovery colorful carousel/card-rail prototype refinement

Use this note when refining a Komuna Discovery approval prototype after feedback about blandness, oversized cards, carousel behavior, mobile rails, topbar fidelity, or light/dark inconsistency.

## Preserve before refining

- Prototype-only scope remains gated: do not modify or deploy the live Discovery route until explicit approval.
- Re-read the current branch `TopNav.tsx` before each topbar revision. Prototype navigation must mirror current destinations and visibility concepts; preserve already-approved toggle treatments unless the user asks to change them.
- Keep `Most Popular`, `New Programs`, and `Open to Join` simultaneously visible as stacked sections. Do not silently replace them with tabs or rename their headings during unrelated data cleanup.
- Use verified program records, assets, and detail routes only. When the static mockup needs more cards than verified records provide, duplicate a verified record and add an HTML comment that duplication demonstrates layout only; never invent identities, routes, locations, counts, ratings, prices, or session frequency.

## Hero carousel semantics

- Show exactly one program slide at a time; all non-active slides must be `hidden` and their links removed from the tab order.
- Include autoplay plus previous/next and dot controls.
- Pause autoplay on hover and while focus is inside the carousel; restart after hover/focus leaves.
- Honor `prefers-reduced-motion` by disabling autoplay and smooth spatial movement.
- Link each slide to its verified real program route and maintain an `aria-live` status for manual changes.

## Card anatomy and density

- Each card is one wrapping anchor. Do not place nested buttons/links or require a separate “View program” action.
- Cards remain vertical on desktop and mobile. Scale media, padding, type, badges, facts, gaps, and radius together so refinement preserves the same ratio rather than merely shrinking width.
- Desktop acceptance: three medium-small vertical cards per category row when requested, readable and not cramped.
- Mobile acceptance: retain the vertical anatomy at a smaller readable size in a native horizontal snap rail.

## Mobile rail behavior

- Use `overflow-x:auto`, inline/x scroll snap, overscroll containment, and a thin/tokenized scrollbar.
- Show previous/next chevrons only when content exists in that direction. Recalculate after scroll, resize, and content-size changes.
- Chevron controls scroll by a useful fraction of the rail and honor reduced motion.
- Keep `html` and `body` on `overflow-x:clip`; only the rail scrolls horizontally.

## Theme and shell consistency

- Every component surface consumes theme tokens. Audit hero, carousel, cards, section headers, trust block, FAQ, and footer in both modes.
- A light theme must remain colorful through restrained warm/terracotta, gold, teal, and indigo tokenized surfaces; do not leave arbitrary dark panels in light mode.
- If the footer should match the topbar, make both reference the exact same semantic surface token rather than copying two equivalent raw colors.
- Preserve approved theme/language toggle markup and styling during navigation or density corrections unless fit requires a minimal responsive adjustment.

## QA sequence

1. Check changed-file scope before publication.
2. Assert exact section headings and absence of tabs/tabpanels.
3. Count cards inside each category and verify requested desktop columns.
4. Enumerate every program href and image source against the verified allowlist.
5. Assert one initial visible carousel slide and the presence of autoplay/manual/pause/reduced-motion logic.
6. Assert whole-card anchor semantics and no nested interactive controls.
7. Assert mobile snap rail, minimalist scrollbar, and conditional chevron state logic.
8. Compare topbar navigation against current `TopNav.tsx`.
9. Verify topbar/footer share the same surface token when requested.
10. Publish with a cache-busting query and verify the public body matches the local artifact.

## Common regression pattern

A focused correction can accidentally alter approved information architecture—for example, data cleanup renaming `Most Popular` to `Featured Programs`. After every delegated revision, independently validate preserved labels and interactions, not only the requested delta.
