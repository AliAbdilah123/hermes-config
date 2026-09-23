# Dedicated-account messaging integration audit

Use this checklist when a product receives messages through one dedicated provider account and routes them to application users.

## Identity boundaries

Keep three actors distinct:

1. **Dedicated inbox** — provider account receiving messages.
2. **Service/test senders** — configured accounts the application can use to send messages.
3. **End-user sender** — provider identity being associated with an application user.

Ownership must be proven by an inbound event originating from the end user's provider-stable sender ID. Automatically sending a verification code from a configured service account to the inbox proves ownership of that service account, not of a username entered by the end user. Check that the stable sender ID captured from the provider event is actually tied to the claimed account.

## Retrieval and runtime wiring

- Trace startup wiring, not merely the existence of a poller or webhook handler.
- A poller that is never started provides no runtime retrieval.
- If polling is intentionally disabled, require evidence that webhook callback verification, event subscription, permissions, and public routing are active.
- Feature flags, forced-disabled configuration, and UI feasibility warnings are evidence that the integration is not production-ready.

## Webhook contract

Verify:

- challenge/verify-token handling;
- HMAC validation over the untouched raw body;
- expected provider object and event shape;
- dedicated recipient ID matching;
- echo/self-event filtering;
- explicit text and attachment policy;
- routing by provider-stable sender ID rather than username;
- idempotency using a provider event/message ID;
- bounded request and message sizes;
- observable failure behavior and safe retries.

## Fallback routing

Unknown senders must map to an explicit inbox owner, quarantine, or observable rejection. A successful webhook response that silently drops the message is a correctness risk. Verify owner configuration reaches persistence and that missing owners are surfaced operationally.

## Evidence standard

Mocked provider tests prove local parsing and request construction only. Live readiness requires a real provider event through the public callback, correct persisted routing, deduplication on replay, and confirmed subscription/permission state. Report these boundaries separately.

## Secret hygiene

Inspect ignored and backup environment files without printing values. Files excluded from Git can still hold live credentials. Recommend rotation and secure deletion when a backup contains tokens or app secrets; Git cleanliness does not remove that risk.
