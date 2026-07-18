# Discovery mobile desktop-card scroll rail

Use this reference when a user wants Komuna Discovery merchandising cards to remain visually consistent with desktop while becoming compact and horizontally browsable on phones.

## Approved interaction pattern

- Preserve the desktop card anatomy: image above content, visibility/category badges, title, metadata, and price row.
- Scale the card down for mobile rather than converting it into a wide side-image row.
- Render each populated category as a horizontally scrollable rail with fixed responsive card widths, e.g. `clamp(168px, 58vw, 210px)`.
- Prefer native CSS scrolling: `overflow-x:auto`, `scroll-snap-type:x mandatory`, `scroll-snap-align:start`, `scroll-padding-inline`, and `overscroll-behavior-inline:contain`.
- Append one semantic, focusable **View all** link tile after the final program card. Match the tile to the card dimensions and route it to the real all-programs destination.
- The end tile should become visible naturally when the user reaches the end of the rail. Do not add scroll-position JavaScript merely to reveal it, and do not make it a sticky overlay.
- On mobile, hide a duplicated header-level View all link if the rail-end tile is the approved sole action. Desktop may retain its header link.
- Keep horizontal overflow inside the rail; the page itself must not scroll horizontally.
- Do not hide the scrollbar unless another clear, accessible scroll affordance remains.

## Smallest implementation path

1. Scope rail overrides under the Discovery category/page so shared `ProgramGrid` consumers do not change.
2. Remove only inline grid declarations that prevent responsive CSS.
3. Reuse `ProgramCard`; add class hooks or a small `viewAllTo`/`showViewAll` option only where needed.
4. Override any shared mobile side-image transformation inside the Discovery rail rather than rewriting the card component.
5. Keep the rail data-driven and append the View all tile only for populated categories.

## Verification

Test at 320, 360, 390, and 430px:

- touch swipe, trackpad, and keyboard scrolling;
- snap alignment and complete visibility of the final tile;
- one View all action per mobile category and correct route;
- no page-level horizontal overflow;
- long EN/ID titles, locations, and prices;
- image fallback and badges;
- visible focus indicators and at least 40–44px actionable targets;
- desktop cards and header-level View all remain unchanged.

## Review artifact rule

When this direction is chosen during plan/design review, update both the canonical plan and the separate static design page. The design preview must visibly demonstrate multiple vertical cards in a rail plus the final View all tile; prose alone is insufficient. Keep implementation gated until explicitly requested.
