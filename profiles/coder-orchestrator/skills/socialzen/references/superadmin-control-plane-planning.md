# Superadmin control-plane planning

Use when planning internal controls for users, quotas/credits, billing switches, integrations, or other global capabilities.

## Inspect first

- Session user shape and server authorization helpers.
- User roles/states, plans, entitlements, and quota accounting.
- Every related backend route, provider call, job, callback, webhook, retry, and mock fallback.
- Every frontend route, navigation item, CTA, banner, setting, return page, and direct URL.
- The real application shell and responsive navigation.
- Existing audit/event and transaction patterns.

## Keep three concepts separate

1. **Operator authorization:** who may use the control plane.
2. **Per-user entitlement:** what one account may consume or bypass.
3. **Global availability:** whether a capability is enabled for anyone.

Frontend visibility is not authorization. Provider credentials being configured is not an operator-controlled feature flag.

## Provider kill switches

Plan backend enforcement first. Enumerate subscription mutations, provider clients, renewals/continuation jobs, callbacks, webhooks, replay paths, and mock behavior. Disabled must fail closed with a stable error and must not fall through to mock success. Decide separately whether read-only status and existing entitlements remain available.

For webhooks, distinguish transport acknowledgement from business mutation. Specify validation, acknowledgement, mutation suppression, privacy-safe logging, and replay policy while disabled.

Frontend capability data is presentation only. Remove or neutralize navigation, CTAs, banners, billing settings, payment return/redirect routes, public checkout links, and direct-route access while retaining backend enforcement against handcrafted requests.

## Quota/credit grants

Prefer an append-only ledger over rewriting usage. Record target, actor, positive bounded amount, scope/period, required reason, and timestamp. Define semantics for free/lifetime, finite paid period, unlimited, exempt, expired, and rollover states. Reuse one effective-limit calculation across reservation, retry, status/dashboard, and admin summaries. Test concurrent grants and write grant plus audit transactionally.

## Security minimum

- Authorize every admin handler server-side.
- Bootstrap initial operators through controlled deployment configuration or an existing identity system; no role-promotion API in V1.
- Use explicit response DTOs; never serialize user rows generically.
- Bound inputs, enforce methods/content types, prevent duplicate submits, and use transactions.
- Write immutable redacted audit records for mutations.
- Use optimistic versions for global switches.
- Verify at least one operator remains after rollout.

## Review artifact

Publish separate plan and static-design pages when UI review is needed. Mirror the current product shell; do not invent a new admin aesthetic. Show user search/list, representative entitlement states, grant fields and resulting allowance, flag consequences, unauthorized/loading/empty/error/conflict/success states, desktop/mobile behavior, a “static proposal, not live” label, and an implementation gate.

## MVP cut

Include user search/list, one safe positive-grant action, one named feature flag, authorization, audit, tests, and rollout verification. Defer impersonation, refunds, arbitrary flags, role editing, destructive actions, bulk grants, quota subtraction, and charts until an approved need exists.

## Acceptance evidence

- Ordinary authenticated users receive 403 and see no admin navigation.
- An operator can search and perform a bounded audited grant; reload preserves it.
- Disabled blocks every backend mutation/provider side effect and every actionable frontend path.
- Existing entitlements follow the approved disabled-state policy.
- Re-enabling restores the flow in provider test mode when available.
- Rollout verifies backup, migration/schema, seeded operator, authenticated E2E, and audit rows.
