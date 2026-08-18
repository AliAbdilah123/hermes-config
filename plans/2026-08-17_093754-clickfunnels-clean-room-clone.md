# ClickFunnels-Style Platform Clean-Room Implementation Plan

> **For Hermes:** Use Codex CLI task-by-task after explicit implementation approval.

**Goal:** Build a legally distinct, production-grade funnel commerce SaaS with feature parity across funnel/page building, checkout, CRM, email automation, analytics, memberships, collaboration, and SaaS administration.

**Architecture:** Start as a modular monolith with asynchronous workers, PostgreSQL, object storage, and a React editor/runtime. Separate the control plane (accounts, workspaces, billing) from the data plane (published sites, contacts, orders, events), and introduce services only when measured load requires it.

**Tech Stack:** TypeScript, React/Next.js, Node.js, PostgreSQL, Redis-backed jobs, S3-compatible storage, Stripe, Playwright, Vitest, Docker, nginx/CDN.

---

## Scope and clean-room boundary

This is a functional clone, not a copy of ClickFunnels source code, proprietary assets, copy, templates, trademarks, or pixel-identical trade dress. Build from public behavior and independently created UX. The supplied signup URL returned HTTP 403 in automated inspection, so its exact current screens and pricing are not treated as verified requirements.

## Product capability map

1. **Identity and workspaces:** signup, verification, login, recovery, MFA/passkeys, organizations, invitations, roles, audit log, consent, account export/deletion.
2. **Plans and SaaS billing:** trials, plans, usage limits, coupons, invoices, payment failures, upgrade/downgrade, cancellation, entitlements.
3. **Sites and funnels:** workspace domains, funnels, ordered steps, variants, SEO, scripts, tracking settings, revisions, draft/preview/publish/rollback.
4. **Visual page builder:** section/row/column tree, responsive breakpoints, drag/drop, editable components, global styles, reusable blocks, undo/redo, autosave, validation, preview.
5. **Template system:** first-party templates, categories, import/export, clone, thumbnail generation, template versioning.
6. **Forms and CRM:** forms, custom fields, tags, lists/segments, contact timeline, imports/exports, deduplication, consent and suppression.
7. **Products and checkout:** products, prices, offers, order forms, taxes, shipping, coupons, order bumps, upsells/downsells, receipts, refunds and disputes.
8. **Email and automation:** broadcasts, sequences, visual workflows, triggers, conditions, delays, actions, templates, unsubscribe, bounce/complaint handling, deliverability setup.
9. **Courses/memberships:** products granting access, courses/modules/lessons, drip schedules, member login, progress and access revocation.
10. **Analytics:** visits, sessions, opt-ins, conversion, revenue, AOV, funnel step drop-off, attribution, UTM, exports, privacy controls.
11. **Integrations:** webhooks, API keys/OAuth, Zapier-style events, payment/email/domain providers, idempotency, retries and replay.
12. **Platform operations:** admin support console, tenant impersonation with audit, abuse controls, job replay, feature flags, observability, backups and disaster recovery.

## Core data model

`users`, `workspaces`, `memberships`, `roles`, `invitations`, `plans`, `subscriptions`, `entitlements`, `usage_counters`, `sites`, `domains`, `funnels`, `funnel_steps`, `pages`, `page_revisions`, `page_variants`, `components`, `templates`, `forms`, `form_submissions`, `contacts`, `contact_fields`, `tags`, `contact_tags`, `segments`, `products`, `prices`, `offers`, `coupons`, `orders`, `order_items`, `payments`, `refunds`, `subscriptions_customer`, `courses`, `lessons`, `enrollments`, `lesson_progress`, `email_templates`, `broadcasts`, `sequences`, `automations`, `automation_nodes`, `automation_runs`, `messages`, `events`, `daily_metrics`, `integrations`, `webhook_endpoints`, `webhook_deliveries`, `api_keys`, `audit_events`.

All tenant-owned records carry `workspace_id`; money uses integer minor units plus ISO currency; externally retried mutations use idempotency keys; deletion policy distinguishes soft-delete, legal retention, and anonymization.

## System boundaries

- **Web app/control plane:** authenticated dashboard, editor, billing and administration.
- **Publishing pipeline:** immutable page revision → validated render artifact → object storage/CDN → atomic route switch.
- **Public runtime:** cached HTML/assets, lightweight forms/checkout/event endpoints; no editor bundle.
- **Domain API:** tenant-scoped business logic and transactional writes.
- **Workers:** email, webhooks, imports, automation timers, image/thumbnail jobs, metric aggregation.
- **Event ledger:** append-only behavioral/business events; analytics derived asynchronously and reconciled against orders/payments.

## Implementation phases

### Phase 0 — Discovery and product contract
- Manually document every accessible ClickFunnels workflow using authorized trial accounts: screenshots, states, field rules, navigation, emails, limits and mobile behavior.
- Build a feature parity matrix with `observed`, `inferred`, `defer`, and source/date columns.
- Interview target users and identify must-match outcomes versus optional parity.
- Define original naming, visual design tokens, privacy policy, terms, acceptable-use policy and IP review.
- **Exit:** approved PRD, state diagrams, route map, design system, threat model and MVP cut.

### Phase 1 — Foundation and tenant isolation
- Create monorepo: `apps/web`, `apps/api`, `apps/worker`, `packages/db`, `packages/domain`, `packages/ui`, `packages/editor`, `packages/events`, `tests/e2e`.
- Add PostgreSQL migrations, tenant-scoped repositories, seed data, transaction helpers and object storage.
- Implement identity, workspace setup, invitations, RBAC, audit events, rate limits, CSRF/session protection and secret handling.
- Add CI: format, types, unit, integration, migration and Playwright smoke checks.
- **Exit:** two tenants cannot access each other's records; backup/restore drill succeeds.

### Phase 2 — SaaS onboarding and subscription billing
- Recreate the behavioral signup journey with original content: plan selection, account, payment/trial, workspace setup, onboarding checklist.
- Implement Stripe customer/subscription lifecycle, webhook verification, idempotent reconciliation, entitlements and usage limits.
- Cover payment failure, SCA, duplicate webhooks, downgrade limits, cancellation and account recovery.
- **Exit:** authenticated public E2E proves trial → paid → failed renewal → recovery → cancellation.

### Phase 3 — Funnel model and publishing
- Implement site/funnel CRUD, ordered steps, page revisions, settings, custom scripts, slugs, preview, publish and rollback.
- Generate immutable static/runtime artifacts and atomically deploy them to tenant domains.
- Add domain ownership verification, TLS automation, redirects, sitemap/robots and cache invalidation.
- **Exit:** a funnel publishes on custom domain, survives rollback, and remains available during editor/API outage.

### Phase 4 — Visual editor
- Use one canonical JSON page tree with schema version and migrations.
- Add selection, drag/drop, insert/delete/duplicate, responsive styles, component inspector, global theme, undo/redo, keyboard/a11y controls, autosave conflict detection and preview.
- Ship minimum components: heading, text, image, video, button, divider, spacer, icon, list, form, countdown, product selector, checkout, navigation and custom HTML under sandbox/CSP rules.
- Add reusable blocks and independent original templates.
- **Exit:** Playwright edits every component, reloads autosave, publishes, compares runtime content and checks mobile overflow/accessibility.

### Phase 5 — Leads and CRM
- Build form designer/runtime, server validation, spam controls, double opt-in, custom domains, contact profile/timeline, tags, static/dynamic segments, CSV import/export and merge/deduplication.
- Record consent source/time/policy and enforce suppression globally.
- **Exit:** public submission creates exactly one contact/event under retries and triggers configured actions.

### Phase 6 — Commerce and funnel offers
- Build catalog, offers, prices, coupons, tax/shipping configuration, checkout, order bump, one-click upsell/downsell, receipts and customer portal.
- Use provider-hosted or tokenized payment elements; never store card data.
- Implement order/payment state machines, refund/dispute handling, webhook reconciliation and ledger reports.
- **Exit:** authenticated public E2E uses provider test payments across success, decline, SCA, upsell, refund and duplicate-webhook paths.

### Phase 7 — Messaging and automation
- Add provider abstraction only for email transport; start with one provider.
- Implement templates, broadcasts, sequences and workflow graph with versioned definitions.
- Triggers: form, tag, purchase, refund, enrollment, date/time and webhook. Actions: email, tag, field update, enrollment, webhook; conditions and delays.
- Add durable scheduling, retries, dead-letter/replay, concurrency control, per-contact deduplication, unsubscribe, bounce and complaint processing.
- **Exit:** deterministic clock-based tests plus sandbox provider E2E prove no duplicate messages.

### Phase 8 — Courses and memberships
- Create course/module/lesson authoring, media, access products, enrollment, drip rules, member portal, progress and revocation.
- Sign private media URLs and enforce enrollment server-side.
- **Exit:** purchase grants access; refund/revocation removes it; drip timestamps are timezone-safe.

### Phase 9 — Analytics and optimization
- Define first-party event schema and consent-aware client/server collection.
- Add funnel conversion, revenue, AOV, step drop-off, source/UTM and date filters.
- Add A/B variants with stable visitor assignment, exposure events, conversion attribution and guardrails.
- Reconcile revenue metrics against payment ledger and monitor event loss.
- **Exit:** synthetic journeys yield mathematically verified dashboards without double counting.

### Phase 10 — Integrations and public API
- Add scoped API keys/OAuth, versioned REST API, signed webhooks, retries, delivery logs and replay.
- Start with the few integrations validated by discovery; do not build a generic marketplace first.
- **Exit:** contract tests, rate-limit tests and webhook consumer fixtures pass.

### Phase 11 — Production hardening and launch
- Security review: OWASP ASVS, tenant escape, SSRF, XSS in editor/runtime, upload scanning, CSP, dependency/SBOM and payment scope.
- Load test publish, public pages, form bursts, checkout and automation queues; define SLOs and capacity thresholds.
- Add dashboards, tracing, alerting, support/admin tools, abuse workflows, retention jobs and incident runbooks.
- Run restore, region/provider outage and rollback exercises.
- Launch via internal tenants → design partners → limited beta → general availability.

## Testing ladder

- Unit: validators, state machines, pricing, entitlements, editor commands and event attribution.
- Integration: PostgreSQL transactions/RLS-like scope, Stripe/email/webhook sandboxes, queues and object storage.
- Contract: OpenAPI, events, webhooks, page JSON migrations and generated artifacts.
- E2E: all critical journeys on authenticated public HTTPS routes in desktop/mobile browsers.
- Non-functional: accessibility WCAG 2.2 AA, visual regression for original UI, performance budgets, security scans, load and restore drills.
- Release gate: migrations reversible/forward-safe, zero critical vulnerabilities, no cross-tenant exposure, RPO/RTO proven, support runbooks ready.

## Suggested delivery slices

- **MVP (16–24 weeks, multi-disciplinary team):** identity/workspaces, billing, basic funnel editor/publish, forms/contacts, Stripe checkout, basic email sequence, essential analytics.
- **V1 (additional 12–20 weeks):** richer editor/templates, upsells, domains, broadcasts/automation, memberships, robust analytics/integrations.
- **Parity program (additional 6–12+ months):** mature ecosystem, advanced optimization, extensive integrations, enterprise controls and operational depth.

These are planning ranges, not commitments; staffing, quality bar and verified parity matrix determine schedule.

## Team shape

Product lead, designer/researcher, tech lead, 3–5 full-stack engineers, platform/backend engineer, QA automation engineer; part-time security, legal/privacy, deliverability and DevOps support. Add dedicated data/analytics and support operations before V1.

## Major risks and controls

- **Unbounded “complete clone”:** versioned parity matrix and explicit acceptance tests.
- **IP/trade dress:** clean-room evidence, original brand/design/copy/assets, legal review.
- **Editor complexity:** constrained schema/components before arbitrary layout capability.
- **Payment correctness:** provider tokens, idempotency, state machines and reconciliation.
- **Email reputation:** consent/suppression, dedicated domain guidance and provider feedback loops.
- **Tenant leakage:** mandatory scope at repository layer, adversarial integration tests and audit trails.
- **Analytics mismatch:** append-only event IDs, attribution contract and ledger reconciliation.
- **Premature microservices:** modular monolith until scaling evidence establishes a boundary.

## Open questions for approval

1. Is the target an MVP competitor, current feature parity, or parity with a specific ClickFunnels edition/date?
2. Which launch market/countries, currencies, tax rules and privacy regimes apply?
3. Must V1 include courses, email delivery, A/B testing, affiliate management and custom domains?
4. Preferred payment/email/domain vendors and cloud region?
5. Expected tenants, contacts, monthly page views, emails and GMV at launch/year one?
6. Required migration/import from ClickFunnels, and what exports are legally available?
7. Budget, team and launch target?

## Definition of done

- Approved parity matrix has no unclassified capabilities and all committed rows have executable acceptance evidence.
- Every primary journey passes authenticated public desktop/mobile E2E.
- Billing and customer payment ledgers reconcile; retries do not duplicate orders, contacts, messages or automation actions.
- Tenant isolation, accessibility, performance, security, backup/restore and incident response gates pass.
- Product uses original implementation, brand, UX expression, copy and assets.

## Implementation gate

This plan authorizes no implementation, subscription purchase, account creation, deployment, or copying. First approve scope and answer the seven open questions; then produce a repository-specific plan with exact files and bite-sized TDD tasks.
