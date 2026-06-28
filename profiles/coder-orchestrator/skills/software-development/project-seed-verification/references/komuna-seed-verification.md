# Komuna seed verification example

This reference captures a reusable pattern from checking whether a migrated project had been seeded with necessary data.

## Situation

The repository contained rich legacy seed files under an older stack:

- `apps/api/src/db/seed.ts`
- `apps/api/src/db/seed-kaltim.ts`

Those files seeded many users, programs, products, packages, sessions, vouchers, claims, audit logs, and notifications, including a large Kaltim coworking/workspace dataset.

However, the active deployed stack was a Go + SQLite API in `api/v1/main.go`, not the old Neon/Drizzle app. The active API seeded state via an in-code `seed() State` function and stored it in SQLite table `app_state` as JSON.

## Verification pattern used

1. Locate seed files and read enough to understand expected dataset scope.
2. Check public health endpoint:
   - `GET /projects/komuna/api/v1/health` returned OK.
3. Check public programs endpoint:
   - `GET /projects/komuna/api/v1/programs?limit=3` returned two programs.
4. Inspect active SQLite database, decode `app_state.payload`, and count arrays.
5. Compare active runtime counts against richer legacy seed script claims.

## Observed active runtime counts

- Programs: 2
- Products: 3
- Packages: 2
- Sessions: 3
- Members: 1
- Vouchers: 2
- Claims: 1
- Requests: 2
- Purchases: 0 / missing array
- Audit logs: 1
- Notifications: 1
- Auth users: 4

Observed programs:

- `prog-box` — Jakarta Fight Club — Kemang, Jakarta
- `prog-yoga` — Bali Sunrise Yoga — Canggu, Bali

## Reporting lesson

The correct verdict was not simply “yes, seeded” or “no, not seeded.” It was:

> Seeded enough for basic demo/testing flows, but not with the full rich production-like dataset available in legacy seed files.

Use this distinction for future project seed checks: **baseline/demo seeded** vs. **full necessary domain dataset seeded**.
