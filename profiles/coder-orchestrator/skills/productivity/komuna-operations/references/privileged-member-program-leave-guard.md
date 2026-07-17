# Privileged member program-leave guard

Use when a program Admin or product-scoped Manager must not leave the program until their privileged assignments are revoked.

## Core invariant

A program membership may transition from `active` to `inactive` only when the member has neither:

- an `admin` or `manager` row in `program_member_roles`; nor
- any assignment in `product_managers` for that membership.

Enforce this in the API. Hiding the UI action is explanatory UX, not the security boundary.

## API pattern

Avoid a separate privilege check followed by an unconditional membership update. That creates a check-then-update race where a role can be assigned between statements.

Use a transaction and one conditional `UPDATE` whose `WHERE` clause includes `NOT EXISTS` checks for both role representations. If zero rows change, inspect authoritative state within the same transaction to distinguish:

- privileged active member → `403` with a stable role-revocation error;
- missing/already inactive membership → controlled `404` or the endpoint's established no-op response.

Do not write a leave audit event when authorization is rejected.

## DTO/capability normalization

Backend authorization and frontend role presentation must recognize the same representations. If `programUserRoles` reads only `program_member_roles`, an assignment-only row in `product_managers` produces a misleading Leave button even though the API correctly rejects it.

Normalize `product_managers` assignments into a deduplicated `manager` role in the program-detail DTO, or expose an API-derived `canLeaveProgram` capability. Prefer the existing role DTO when it can be normalized with a compact query; add a new capability only if role semantics are otherwise ambiguous.

## UI behavior

For an active ordinary member, retain **Leave Program**. For privileged members, preserve normal member actions such as booking but replace the destructive action with concise role-aware text:

- `You’re an admin. Revoke your role to leave.`
- `You’re a manager. Revoke your role to leave.`
- `You’re an admin and manager. Revoke your roles to leave.`

Localize the copy. Avoid a disabled unexplained button.

## Regression matrix

Write tests before implementation and watch them fail:

1. Ordinary active member can leave.
2. Admin receives `403`; membership stays active; no leave audit is written.
3. Manager represented by `program_member_roles` receives `403`.
4. Manager represented only by `product_managers` receives `403`.
5. Program-detail DTO returns `manager` for assignment-only managers.
6. A manager represented in both tables receives one deduplicated role.
7. React UI shows Leave for ordinary members.
8. React UI replaces Leave with Admin, Manager, and combined-role messages while retaining other member actions.

After tests/build, independently review the diff specifically for representation drift and check-then-update races before deployment.
