# Debug-first authorization and recovery

When a user asks to **debug**, treat the task as read-only until they explicitly authorize implementation/deployment.

## Required sequence

1. Reproduce and trace evidence only: endpoints, queries, UI source, runtime values.
2. Report root cause and the exact proposed change.
3. Wait for explicit implementation wording before editing, committing, or deploying.
4. If you already made an unapproved fix, stop immediately, revert that change, redeploy the previous behavior if it was deployed, then re-debug from evidence before applying any newly-authorized fix.

## Voucher/count class pitfall

For member-facing counts, distinguish **tenant/program inventory** from **current user's owned entitlements**. A program-wide active voucher count can be correct for admin inventory while wrong for member banners, wallet hints, booking modals, and member dashboards.

Probe both sides before fixing:

- UI endpoint/component feeding the visible count.
- DB count of program-wide active vouchers.
- DB count of active vouchers joined through `program_members` for `pm.user_id = current user` and current program.
- Wallet endpoint behavior: wallet may intentionally aggregate across programs while program banners stay scoped to the viewed program and signed-in user.

Smallest root fix: scope member-facing voucher summary/dashboard queries through `program_members` and `user_id`; leave admin inventory queries program-wide.