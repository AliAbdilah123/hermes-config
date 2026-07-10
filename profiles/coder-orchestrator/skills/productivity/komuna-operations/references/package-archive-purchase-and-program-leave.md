# Package archive purchase surfaces + canonical program leave

Use when fixing Komuna public/member purchase flows around archived `PurchasePackage` rows, or when public routes use slugs while member APIs require canonical IDs.

## Durable checks

- Archived packages must remain visible to admin/history screens, but not public/member purchase surfaces.
- Public store/package cards should filter to `pkg.status === 'active'` even if the shared package list endpoint returns archived rows for admin/history use.
- Direct checkout URLs for archived packages must fail closed before quote/payment UI. Treat the package as unavailable/not found and do not call `/checkout/quote` or `/checkout` from the web page.
- Server-side checkout must also block archived packages in the shared pricing/prepare path, not only in UI. Komuna's checkout service pattern is a single guard like `pkg.package.status !== 'active' -> package_unavailable` before membership/fee/purchase creation.
- Program leave actions should use the canonical `program.id` loaded from the API response, not the route param, because public routes may contain slugs.

## Regression tests to leave behind

- Public program page hides an archived package returned by package data.
- Direct `/programs/:id/packages/:packageId/checkout` for an archived package renders package unavailable/not found and does not request a quote.
- A slug route such as `/programs/eastside-boxing` still calls `leaveProgram(program.id)` with the canonical id returned by `/programs/:slug`.

## Deployment note

For live nginx-hosted Komuna web changes, `npm run build` in `apps/web`, then copy `apps/web/dist/` to `/var/www/html/projects/komuna/` and verify `https://komuna.ahsanworks.com/...` returns 200.
