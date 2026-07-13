# Admin Analytics Contract Notes

Use when explaining, debugging, or extending the Komuna admin Analytics tab.

## Current API shape

The admin Analytics page fetches:

- `GET /programs/:programId` for program metadata.
- `GET /programs/:programId/analytics` for summary analytics.

The backend analytics service currently calculates summary-level fields only:

- `revenue` — total paid purchases by program members.
- `attendanceRate` / DTO `attendance_rate` — present claims divided by non-cancelled claims for sessions in the date window.
- `noShowRate` / DTO `no_show_rate` — absent claims divided by non-cancelled claims.
- `voucherUtilization` / DTO `voucher_utilization` — claimed vouchers divided by total vouchers for the program's products.
- `compensationRate` / DTO `compensation_rate` — cancelled claims with compensation vouchers divided by cancelled claims.
- `packageAttribution` / DTO `package_attribution` — package id/name/revenue rows.

## Frontend mismatch pitfall

The React Analytics page renders richer chart/table sections than the API currently returns. Several fields are intentionally filled with empty arrays/zeros in `mapApiToPageData`, including monthly revenue, revenue by product, attendance charts, no-show trend/worst products, voucher status counts, voucher utilization by product, compensation trend/reasons, and package sales metadata.

If a screenshot shows KPI cards with data but empty charts, first check whether the chart data is simply not implemented in the API yet before treating it as a data-loss bug.

## Percentage pitfall

The backend service's percentage helper already returns `0–100` values. If the frontend displays values like `8000%`, look for a second multiplication by 100 in the UI mapping layer. The correct display mapping should not multiply backend percentage DTOs again unless the contract has explicitly changed to fractions (`0–1`).

## UX explanation pattern

When asked "what does analytics fetch/want?", explain the source tables/concepts and clearly separate:

1. What the API really provides today.
2. What the UI is rendering as future/placeholder analytics.
3. Any immediate contract bug, especially percentage scaling or camelCase/snake_case DTO mismatch.
