# Product route slug resolution and manager scope

Use when a Komuna manager/product page shows a generic **Product** title or zero child records even though the product has sessions.

## Diagnostic signature

The browser route may carry a canonical product slug while older Go handlers query `product_id` directly. Reproduce both forms against the same endpoint:

- internal ID returns rows;
- canonical slug returns an empty collection;
- frontend product lookup by ID only falls back to a generic title.

Trace the route parameter through every related request (dashboard, sessions, claims, approvals) rather than patching only the visible list.

## Safe resolver contract

Resolve products inside the requested program:

1. Check an exact `(program_id, product.id)` match first.
2. Otherwise query `(program_id, product.slug)` with a limit of two.
3. Resolve only one slug match.
4. Treat missing or duplicate slugs as unresolved; return controlled `404`.
5. Never return the raw route value after failed resolution.

ID-first handling avoids ambiguity when one product's slug equals another product's ID. Unique-match handling avoids nondeterministic `QueryRow` behavior because legacy schemas may not enforce slug uniqueness.

## Filter pitfall

If a shared resolver returns an empty string for unresolved input, distinguish:

- no `productId` filter supplied: list all program sessions;
- filter supplied but unresolved: return `404` (or an intentional empty result).

Do not interpret both as “no filter,” or a foreign/invalid product filter can disclose all sessions in the program.

## Manager authorization

Manager dashboard and claim endpoints must authorize after strict product resolution. Permit only:

- platform admin;
- active program admin membership;
- active product-manager membership assigned to the resolved product.

Inactive/suspended memberships must not retain scoped authority. Keep all product/session/claim queries program-scoped even after authorization.

## Regression matrix

Add tests before the fix and watch them fail for:

- slug differs from internal ID and returns the expected sessions/dashboard/claims;
- existing ID route still works;
- foreign-program ID and slug return `404`;
- ordinary authenticated member receives `403` on manager endpoints;
- inactive admin receives `403`;
- active assigned manager succeeds;
- platform admin succeeds;
- duplicate slug is unresolved;
- exact ID wins over a matching slug;
- supplied invalid product filter does not become an unfiltered list;
- omitted product filter preserves intentional all-program behavior.

Run Go tests/build plus the focused manager-dashboard frontend test. After deployment, verify the live slug endpoint returns real rows—not merely HTTP 200—and confirm the API service remains active.
