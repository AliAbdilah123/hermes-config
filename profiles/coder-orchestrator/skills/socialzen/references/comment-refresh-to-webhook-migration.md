# Migrating provider comment refresh to webhooks

Use this when SocialZen fetches Instagram/Facebook comments when a user opens a view or presses Refresh.

## Endpoint separation

Never reuse an OAuth redirect callback as a webhook endpoint. OAuth callbacks receive browser redirects with authorization state/code; webhooks receive provider verification challenges and signed event deliveries. Give each provider a dedicated webhook path, for example:

- `/api/integrations/instagram/webhook`
- `/api/integrations/facebook/webhook`

Keep routes such as `/api/facebook/oauth/callback` OAuth-only.

## Migration sequence

1. Add dedicated GET challenge and POST delivery routes before changing the UI.
2. Verify the challenge token and `X-Hub-Signature-256` over the exact raw POST bytes with the provider app secret.
3. Bound body size and accepted object/change types.
4. Durably deduplicate deliveries by provider event/change identity.
5. Resolve provider account/page and media/post IDs through existing connected accounts and published targets; never derive tenancy from client claims.
6. Apply only the referenced create/update/delete/reply mutation. Do not run full-list deletion reconciliation for one webhook event.
7. Subscribe accounts/pages during connection and repeat on reconnect/token replacement. Do not advertise readiness when subscription fails.
8. Remove provider refresh calls from read endpoints and frontend mount/click behavior only after webhook delivery is verified.
9. If the open UI needs freshness without SSE/WebSockets, poll the local database endpoint modestly and on focus; never turn that into provider polling.
10. Retain pull sync temporarily behind an authenticated admin/worker recovery path, then retire it after webhook reliability is established.

## Event-processing rules

- Handle duplicate and out-of-order delivery.
- Preserve provider parent-comment identity when a reply arrives before its parent, then link later.
- Use provider event timestamps/version semantics where available so stale updates cannot overwrite newer state.
- Unknown accounts/posts should be safely acknowledged and recorded for diagnostics without leaking tenant data.
- Return retryable 5xx when durable receipt or mutation storage fails; acknowledge verified duplicates successfully.
- Logs may include provider, safe event key, and result, but not access tokens, signatures, full payloads, or comment text.

## Deployment and verification

- Before restarting, ensure both server-only verification tokens exist in the service environment; generate strong random values when provisioning, never print them, and never expose them through config/status APIs.
- Build the Go binary to a temporary path, install it atomically into the service location, deploy the clean frontend `dist/`, restart, and health-check before public probes.
- Probe each public GET callback twice: an incorrect token must return `403`, while the configured token must echo a unique challenge with `200`. Use `curl --data-urlencode` (or equivalent) so shell quoting in environment files cannot corrupt token comparison.
- Exercise each POST callback with an exact-byte HMAC fixture. A signed unknown-ownership event should be acknowledged without creating a comment; an altered payload or signature must fail.
- Public route probes and synthetic signed fixtures prove routing, verification, and safe unknown-owner handling only. They do **not** prove provider subscription or real ingestion. Do not report READY until Meta dashboard callbacks/subscriptions are configured and fresh real Instagram and Facebook comments appear in the deployed UI without a refresh POST.

## Verification coverage

Test challenge success/failure, altered raw bytes, missing/malformed signature, oversized/malformed payloads, duplicates, stale ordering, child-before-parent, unknown/disabled accounts, cross-tenant isolation, create/update/delete/reply for each provider, OAuth callback regression, and proof that opening the comment UI performs local reads without refresh requests.
