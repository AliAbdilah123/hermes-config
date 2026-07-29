# Compact cards with rich-text descriptions

## Trigger

Use when a review replaces compact card facts such as price/status with a program, product, or listing description sourced from an API.

## Minimal implementation

1. Inspect the DTO/schema and existing detail-page renderer to determine whether the description can contain HTML.
2. Search for and reuse the existing sanitizer/plain-text conversion helper.
3. Convert at the compact-card boundary and render the resulting string as React text; do not use `dangerouslySetInnerHTML` merely to fill a preview card.
4. Apply the line clamp to the normalized text and keep the existing card dimensions/aspect ratio.
5. Remove obsolete metadata from both visible DOM and accessible names. Preserve explicitly retained facts such as category/location.

## Focused check

- Use a fixture such as `<p>Practice <strong>together.</strong></p>` and assert the card displays `Practice together.` with no markup text.
- Assert removed price/status labels, badges, fallbacks, and accessible-name fragments are absent.
- Render the exact public desktop and mobile routes using real API records; inspect for raw `<h2>`, `<ul>`, `<li>`, and entity fragments.
- Treat partial next-card exposure in a horizontal rail as intentional only when the exposed card's internal layout remains coherent.

## Pitfall

A passing unit test with a plain-text description does not prove production rich-text records render correctly. Real-data browser proof is the gate that catches raw HTML tags in compact cards.
