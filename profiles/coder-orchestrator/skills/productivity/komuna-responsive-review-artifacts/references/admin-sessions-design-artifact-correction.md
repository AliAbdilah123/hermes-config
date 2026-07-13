# Admin Sessions Design Artifact Correction

Session learning from Komuna admin dashboard Sessions page review artifacts.

## Correction captured

When the user asks for both a **design** and a **plan**, do not combine them into one page unless explicitly requested. Publish separate review artifacts:

- `...-plan.html` — text requirements, implementation notes, acceptance criteria.
- `...-design.html` — visual design/mockup only.

For admin/dashboard page designs, the design artifact must show a **full-page dashboard context**, not an isolated small product/card mockup. Reuse and visually remodify the actual app component structure/class language where known, e.g. for the Sessions tab:

- `sessions-tab-page`
- `sessions-tab-head`
- `sessions-product-card`
- `sessions-product-head`
- `sessions-row`
- status pills
- action buttons
- detail panels

If the user asks for desktop and mobile, keep them on the **same design page** with desktop first and mobile below it, unless they asks for separate pages. The mobile section should be a stacked version of the same component system, not an unrelated mobile-only concept.

## Sessions page hierarchy pattern

When revising the Sessions page after instructor/product feedback, prefer this hierarchy:

- Remove wording like “template” from user-facing session cards/rows unless the user explicitly asks to expose implementation concepts.
- Make the product/session family title the dominant information, e.g. `Sunrise Vinyasa` should be visually stronger than its generated/session rows.
- Render upcoming sessions as compact line rows, not large cards that compete with the main product title.
- Put the disclosure chevron/arrow icon at the left edge of the product row instead of a right-side text button like “Collapse”.
- Show at most the next 5 upcoming sessions in the collapsed/summary area.
- Put deeper product/session metadata below the row list behind a clear `See detail` section.

## Pitfall

Avoid producing a generic pretty concept page for a dashboard redesign. The user expects the review artifact to reflect the real product surface and component vocabulary so approval can map directly to implementation.

Do not let generated/upcoming session instances dominate the parent product information. The main product/session family label is the page anchor; individual upcoming sessions are supporting rows.
