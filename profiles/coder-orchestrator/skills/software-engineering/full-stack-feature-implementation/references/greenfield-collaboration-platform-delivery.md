# Greenfield real-time collaboration platform delivery

Use for Slack/Teams/Discord-class product requests where the user asks for a complete white-label application, real-time messaging, and third-party integrations.

## Scope translation

- Do not promise an undifferentiated “all features” clone. Translate it into an original, white-label product with a feature-parity roadmap and explicit deferred enterprise capabilities.
- Avoid proprietary branding, copyrighted assets, exact visual replication, and undocumented protocol compatibility. Preserve collaboration concepts while creating an original interface and API contract.
- Establish the V1 boundary before implementation: identity/workspaces, channels and DMs, durable messaging, real-time delivery, threads/reactions, files/search, notifications, roles, branding, apps/OAuth/API/webhooks, administration, and hardening.

## Architecture default

Start with a modular monolith unless measured scale requires otherwise:

- React/TypeScript web client.
- One stateless API service with WebSocket support.
- PostgreSQL for durable state and permission-aware search.
- Redis for ephemeral presence, typing, and cross-instance fan-out.
- S3-compatible object storage for files.
- Transactional outbox for notifications, indexing, and webhook delivery.

Keep tenant authorization explicit with `workspace_id` on every tenant-owned record and membership checks in API reads, WebSocket subscriptions, search, files, notifications, exports, and webhook fan-out.

## Ordered delivery

1. **Executable skeleton:** repository, health endpoints, environment validation, migrations, local dependencies, OpenAPI seed, CI, production builds.
2. **Identity and tenancy:** sessions, workspaces, invitations, roles, authorization matrix, cross-tenant denial tests.
3. **Durable messaging:** channels, DMs, membership, message CRUD, cursors, read markers, drafts.
4. **Real time:** authenticated WebSockets, event cursor/resume, reconnect catch-up, presence expiry, unread state.
5. **Collaboration:** threads, mentions, reactions, saved items.
6. **Files and search:** signed upload/finalize, authorized download, cleanup, permission-safe indexing and filtering.
7. **Notifications:** in-app/email/browser preferences, mute, DND timezone boundaries, deduplication.
8. **Developer platform:** OAuth authorization code + PKCE, scoped expiring tokens, bot identities, incoming webhooks, signed outgoing events, retry/dead-letter/replay, OpenAPI examples.
9. **Brand/admin/release:** branding, audit, retention basics, quotas, threat model, backups, accessibility, load checks, public authenticated E2E.

Advance one milestone at a time. Delegate only the current milestone and prohibit later scope, commits, pushes, deployment, and plan edits. Independently inspect and rerun each gate before advancing.

## Integration security invariants

- OAuth redirect URIs use exact matching; require PKCE for public clients.
- Hash access tokens at rest; scope, expire, rotate, and revoke them.
- Sign outbound webhooks with timestamped HMAC; enforce replay windows and stable event IDs.
- Retry deliveries with jitter and idempotency; keep attempt logs and dead-letter/replay state.
- Incoming webhook URLs are secrets and must be rotatable and rate-limited.
- Link previews and webhook callbacks must block loopback, private/link-local networks, unsafe schemes, and redirect-to-private SSRF.
- Never let object IDs bypass workspace/conversation membership checks.

## Verification discipline

- Capture RED evidence for behavioral code before implementation.
- If an optional runtime is unavailable, verify every available native/static gate and report only that specific execution gap; do not claim container or deployment success.
- A worker result is a claim. Rerun focused tests, full tests, typecheck/lint, production builds, migration checks, and health probes from the final workspace.
- READY requires public authenticated multi-user E2E, including reconnect/catch-up, authorization denial, mobile layout, and console errors.

## Pitfalls

- Waiting indefinitely for broad “plan approval” after the user explicitly says to continue; that instruction is the implementation gate opening. Take the next ordered milestone.
- Implementing app/webhook infrastructure before tenancy and messaging authorization are proven.
- Splitting into microservices before load or ownership boundaries justify the operational cost.
- Treating WebSocket fan-out as persistence; durable writes and resumable event cursors must remain authoritative.
- Calling an app “fully working” after scaffolding or one milestone. Report milestone status, not product completion.
