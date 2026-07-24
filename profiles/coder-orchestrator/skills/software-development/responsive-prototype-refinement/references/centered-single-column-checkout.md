# Centered single-column checkout preview

Use this pattern when a two-column checkout is requested as a centered vertical flow and user approval is the done definition.

## Structure

- Keep production behavior untouched until the preview is approved.
- Render package details first and payment/order details directly below.
- Put both surfaces in the same single-column parent; do not independently size the cards.
- Give the parent a responsive centered width such as `width: min(100% - 40px, 760px); margin-inline: auto`.
- Give each card `width: 100%`; this guarantees identical edges without duplicated width values.
- Preserve the information hierarchy and payment semantics; this is a layout refinement, not a checkout-flow rewrite.

## Responsive polish

- Reduce outer gutters and card padding at the mobile breakpoint.
- Check breadcrumb wrapping; shorten or collapse it when the final crumb becomes orphaned.
- Keep metadata and trust copy readable against dark surfaces.
- Avoid sticky payment-card behavior once it sits below package details unless it still serves a demonstrated need.

## Approval and verification

1. Publish an isolated, non-transactional preview using representative checkout content.
2. Capture desktop and mobile screenshots from the exact public URL.
3. Verify visually that the shell is centered, the flow is strictly one column, both cards share left/right edges, and there is no overflow or clipping.
4. Before committing, run a temporary `/tmp/hermes-verify-*` script that asserts the viewport, one-column rule, shared shell width, two card instances, and mobile breakpoint; remove it via a cleanup trap.
5. Describe this as ad-hoc targeted verification, not full-suite green.
6. Share the preview link and explicitly state that production implementation awaits approval.
