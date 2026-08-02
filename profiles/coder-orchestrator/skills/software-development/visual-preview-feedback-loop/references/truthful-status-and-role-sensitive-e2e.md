# Truthful status and role-sensitive preview E2E

## Status reporting

- Say `WORKING` only while a tool, process, or agent is actively executing.
- Say `VERIFYING` only while an exact verification is actively running; name it.
- Say `STOPPED` or `PENDING VERIFICATION` whenever no work is running.
- Say `READY FOR REVIEW` only after exact authenticated public-preview E2E passes.
- Never send a progress label and silently stop. Report the transition when execution ends.

## Role-sensitive workflow proof

Tests, builds, health checks, and unauthenticated route probes do not prove role workflows. Exercise the public preview under the real authenticated role context and inspect persisted state before and after each transition.

For approval workflows, prove this sequence:

1. Request returns pending.
2. Target remains unchanged and unassigned before approval.
3. Request appears in every required role inbox.
4. Approval/rejection updates the request.
5. The target changes only after approval.
6. Notifications deep-link to the correct role-specific inbox and automatically reveal the relevant item.
7. Click the actual rendered notification-dropdown item and assert the destination route plus opened inbox state. A correct stored/generated `action_url` is not proof that the dropdown consumes it.
8. Cover legacy notifications whose body predates structured links. If their `target_id` identifies the workflow record, derive a safe internal role-specific URL at DTO serialization time; keep an explicitly stored safe internal URL as the precedence path. Never silently fall back workflow notifications to a generic notifications page.

Dual-role accounts are a required edge case. An overloaded endpoint may prioritize broad Admin authority even when called from Manager UI. Prefer a dedicated request-only contract that cannot perform direct activation, then test a dual-role account through the public endpoint and database.