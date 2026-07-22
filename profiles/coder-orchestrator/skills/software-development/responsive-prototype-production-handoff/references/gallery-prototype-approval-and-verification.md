# Gallery prototype approval and verification

Use for image-gallery work where the user explicitly requires a prototype before production implementation.

## Approval boundary

A short “go ahead” after design-context questions accepts the inferred audience, use case, and tone and authorizes the separate prototype. It does not authorize production changes when the original brief explicitly gates implementation on prototype review. Publish the prototype, collect approval, then implement.

## Prototype fidelity

- Show the relevant real application shell and navigation context.
- Preserve exact requested ordering, such as Gallery immediately before Settings.
- Make requested grid geometry measurable: three `minmax(0, 1fr)` columns and 4:3 items.
- Put the add control in the literal first grid position, with accessible button semantics and requested copy.
- If the production feature changes a carousel, state the data/order contract in the prototype; for example, thumbnail first and gallery images afterward.
- Include deliberate narrow-screen layouts instead of merely scaling desktop columns.

## Pre-handoff probe

Creative approval should precede production lint/tests, but a published prototype still needs focused structural evidence. Generate a temporary verifier with an OS-safe `/tmp/hermes-verify-*` path, assert viewport support, navigation order, grid/aspect-ratio rules, first-item placement, required copy, responsive breakpoints, and any stated carousel-order contract. Run and remove it.

Call this “ad-hoc structural verification,” never “suite green.” Separately verify publication with local/public HTTP status checks. Screenshot QA is preferred when browser tooling is ready; a browser setup failure does not invalidate successful structural and HTTP checks, but it must not be represented as visual verification.
