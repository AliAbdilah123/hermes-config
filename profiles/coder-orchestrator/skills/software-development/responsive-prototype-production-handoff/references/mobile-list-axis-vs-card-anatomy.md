# Mobile list axis vs. card anatomy

Use when a mobile session/catalog page is reported as “scrolling cards horizontally” or the user asks for cards to “load vertically.”

## Distinguish the two layers

- List axis: how sibling cards are arranged. The requested fix is usually a full-width column with no list-level horizontal scrolling.
- Card anatomy: how image, copy, metadata, and actions are arranged inside one card. Preserve this unless the user explicitly asks to redesign the card itself.

A common wrong fix changes each card from image-left/content-right into an image/body/button stack. That does not fix a parent rail whose children still have fixed flex-basis or horizontal overflow.

## Minimal scoped fix

Scope overrides to the page and mobile list, not the shared card globally:

```css
@media (max-width: 900px) {
  .page-root .mobile-list {
    width: 100%;
    flex-direction: column !important;
    overflow-x: visible;
  }

  .page-root .mobile-list .card {
    width: 100%;
    max-width: 100%;
    min-width: 0;
    flex: 0 0 auto;
  }
}
```

Inspect shared responsive rules for fixed `flex-basis`, `min-width`, `overflow-x:auto`, snap behavior, and `!important`. Override only the list-level declarations that force a rail.

## Verification

At the acceptance viewport, verify rendered geometry rather than only CSS text:

1. Every sibling card has approximately the list’s full content width.
2. Successive cards have increasing `top` coordinates and approximately equal `left` coordinates.
3. The list and page satisfy `scrollWidth <= clientWidth`.
4. The image and body inside each card retain the approved horizontal anatomy.
5. Desktop/shared card layouts are unchanged.

A source assertion can guard selector intent, but it is not visual proof. Keep one focused regression check and supplement it with DOM geometry or screenshot QA before deployment.
