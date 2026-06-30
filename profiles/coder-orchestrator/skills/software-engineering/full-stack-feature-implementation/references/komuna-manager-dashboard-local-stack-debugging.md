# Komuna local-stack manager dashboard debugging

Use this when Komuna's migrated local Go + SQLite/JSON-state API shows manager dashboard errors, missing assigned products, stale workspace routing, or confusing mobile dashboard layout.

## Durable lessons

- Workspace role DTOs must match the React client shape. The local Go API may store or naturally emit snake_case fields such as `product_id`, but the Vite client expects role assignments with `productId` and `productName`. If a product manager sees `No assigned product available` despite correct DB state, inspect `/me/workspace` first and verify the role object shape.
- Add frontend normalization only as a compatibility guard; still fix the API DTO so deployed clients receive camelCase fields.
- For single-program product managers, `/dashboard` should route directly to the manager/product path when there is one clear manageable choice. Avoid keeping them on a workspace chooser unless they have multiple choices or mixed admin/manager roles that make the choice meaningful.
- A minified browser error like `e is not iterable` can come from a wrong API envelope, not just frontend state. For the manager dashboard, the route `/programs/:programId/manage/products/:productId/session-claims` must return `{ data: ManagerSessionClaimDTO[] }`; returning the dashboard summary object makes `claimsData.data` undefined and breaks iteration.
- Regression-test API envelopes for local compatibility shims, especially routes whose path prefixes overlap (`/manage/products/:productId/dashboard` vs `/manage/products/:productId/session-claims`).

## Mobile layout checklist for this page class

- Session cards should not use a desktop `auto 1fr auto auto` row on narrow screens. Reflow to a two-row grid: date/body first, then actions; stack actions full-width at very narrow widths.
- Set `min-width: 0` on grid/flex children and use `overflow-x: hidden/clip` at the page wrapper to prevent clipped right-side action buttons.
- Keep time ranges readable; allow controlled wrapping rather than squeezing `1:37 PM – 2:37 PM` into multiple awkward columns.
- Long status chips such as locked/session-ended must wrap or occupy a full action row; never let them clip off the card edge.
- Pending approval rows should stack identity, chip, and approve/deny actions on mobile with full-width touch targets.
- Add bottom padding for mobile browser/navigation bars so pending cards are not hidden.

## Verification pattern

1. Query the public/local API with the affected user header or auth token and check exact JSON shapes:
   - `/api/v1/me/workspace`
   - `/api/v1/programs/<program>/manage/products/<product>/session-claims`
2. Add targeted Go tests for DTO/envelope shape and targeted web tests for route/component behavior.
3. Run `go test ./...` in `api/v1`, the relevant Vitest file(s), and `npm run build` in `apps/web`.
4. Deploy both layers as needed: rebuild/restart the Go service for API fixes; rsync the Vite `dist/` to the nginx public project path for frontend fixes.
5. Curl public `index.html` plus hashed JS/CSS assets and grep for route/layout markers when browser login is impractical.
