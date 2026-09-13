# Versioned Bundle Menu Integrity

Use when a versioned catalog adds composite/bundle products.

## Minimal contract

- Persist bundle `kind` and versioned `{menuId, quantity}` components; price remains the bundle's explicit sale price.
- Require at least two components and positive integer quantities.
- Reject self-reference, missing components, archived components, and cycles. The smallest safe cycle policy is to allow standard-item components only and reject nested bundles.
- Keep prior bundle versions immutable when editing.
- At checkout, snapshot the sold bundle's name and custom price as one ordinary order line; do not rebuild historical orders from the current catalog.

## Read and privacy behavior

- Admin views may show full composition.
- Cashier/display details may show component names and only explicitly public component ingredients.
- If a component is archived after bundle creation, retain the bundle and historical version for audit, but mark the current bundle unavailable for sale and explain the broken composition in details.

## Focused regression matrix

1. Valid two-component bundle saves and renders its quantities.
2. One component, zero/fractional quantity, self-reference, nested bundle, missing component, and archived component are rejected.
3. Bundle enters the cart at its custom price; tax/discount calculations use that price.
4. Completed order keeps the original bundle name and price after catalog mutation.
5. Archiving a component disables the bundle without hiding its composition.
6. Public details include public component ingredients and exclude hidden ones.

Prefer a shared pure validator used by both authoring and saleability checks, so persisted data that later becomes invalid is handled at the read boundary too.