# Komuna Product Manager Sessions — Concrete Reference

## Shared frontend path

- Manager entry: `apps/web/src/pages/ManagerSessionsPage.tsx`
- Admin entry: `apps/web/src/pages/dashboard/SessionsTab.tsx`
- Shared view: `apps/web/src/pages/dashboard/admin-sessions/SessionsTabView.tsx`
- Shared controller: `apps/web/src/pages/dashboard/admin-sessions/useAdminSessions.ts`
- Occurrence mapping: `apps/web/src/pages/dashboard/admin-sessions/sessionModel.ts`
- Shared row/calendar: `apps/web/src/prototypes/admin-sessions/PrototypeSessionRow.tsx` and `PrototypeSessionCalendar.tsx`
- Shared dialogs/panels: `PrototypeAttendancePanel`, `PrototypeDeactivationDialog`, `PrototypeManagerPicker`

The manager entry passes `productId` and authenticated `managerUserId` into the shared controller. Product-scoped loading intentionally avoids fetching the full program member directory.

## Required adaptation

- Manager activation should use the same generated-occurrence and refresh path as Admin, but self-assign through server-derived identity rather than open the manager picker.
- Remove the inline unawaited manager activation closure in the shared view.
- Keep Admin's manager picker and reassignment behavior unchanged.
- Own active occurrences expose attendees and deactivate.
- Foreign-owned active occurrences render one locked status cell and no action controls.
- Keep exactly five direct children in the compact row grid; place lock text inside the existing status cell rather than adding a sixth sibling.
- Resolve display identity with `manager?.name ?? occurrence.managerName`; do not broaden member-directory access.

## Existing backend authority tests

`api/v1/session_manager_ownership_test.go` already provides useful patterns for:

- server-derived manager ownership on activation;
- competing activation conflict;
- owner-only deactivation;
- attendance restricted to owning manager or admin;
- inactive manager rejection;
- terminal/ended session activation rejection;
- atomic reactivation of a released cancelled session;
- reassignment method restrictions.

Extend only uncovered behavior; do not duplicate this suite.

## Legacy schema failure pattern

The manager Sessions tab first loads products. A runtime database created before `products.max_validity_extension_date` and `products.cancellation_tiers` existed can return `db_error` because the list query selects those columns. Fresh databases pass because the current `CREATE TABLE` includes them.

Fix startup migration with duplicate-safe `ALTER TABLE products ADD COLUMN ...` statements and test by:

1. creating a legacy `products` table without those fields;
2. running `NewApp()` against it;
3. inserting a session product;
4. invoking the real product-list handler;
5. asserting HTTP 200 rather than `db_error`.

## Public E2E

Authenticate as the product manager and visit:

`/programs/:programId/manage/products/:productId/sessions`

Then verify:

1. activate an inactive occurrence;
2. refreshed row is Active and names the authenticated manager;
3. attendees opens for the owned occurrence;
4. deactivation with a reason succeeds when lifecycle permits;
5. another manager's active occurrence stays locked;
6. no failed product/session API calls, console errors, or generic `db_error` text;
7. repeat at 390px to catch action/grid overflow.

A page-load screenshot proves only rendering. Do not claim functional verification unless mutations were exercised and persisted.