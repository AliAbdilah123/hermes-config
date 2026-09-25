# Dedicated social inbox identity verification

Use this checklist when one provider account receives messages on behalf of many application users.

## Core ownership invariant

A verification code proves ownership only when the pending user sends it **from the social account being connected** to the dedicated inbox. Never send that code automatically from an application-controlled/test sender: the webhook would bind the controlled sender ID, not the user's account.

On a valid signed inbound event:

1. Match the webhook `recipient.id` to the configured dedicated inbox.
2. Hash the inbound text and atomically match one pending, unexpired, unused code.
3. Persist the webhook `sender.id` as the verified stable provider identity.
4. Consume the code in the same transaction.
5. Do not create a note/message from the verification event.
6. Deduplicate by provider message ID and prevent one provider sender ID from claiming multiple users.

User-entered usernames are labels and collision hints, not provider-backed identity proof. Route later messages by stable provider sender ID.

## Webhook and fallback gates

- Verify the provider signature over the exact raw request body before parsing.
- Ignore echoes, self-events, malformed events, empty text, unsupported message types, and events for other recipients.
- Keep recipient matching based on `recipient.id`; an envelope/entry ID may differ.
- For an unknown sender, save fallback content only to an explicitly configured inbox owner.
- Resolve and bind that owner during startup. If the inbox is configured but its owner does not exist, fail startup clearly instead of acknowledging events that will be silently discarded.
- Preserve message-ID uniqueness so provider retries are idempotent.

## Configuration hygiene

Choose one inbound mechanism. If production is webhook-only, remove dead polling code and poll-specific settings instead of leaving a misleading second path. Remove application-controlled sender credentials once verification is manual. Keep only credentials needed by the dedicated inbox for provider API calls or verification replies.

Do not inspect or print real environment files during code review. Tests should use synthetic config files and fake tokens.

## TDD sequence

1. RED: registration performs zero outbound provider calls and returns a visible code plus inbox identity.
2. RED: signed webhook from sender A activates the pending identity with sender A's stable ID.
3. RED: verification event creates no note; replay is idempotent; expired/reused codes do not activate.
4. RED: subsequent text from sender A creates exactly one note for the correct user.
5. RED: unknown sender fallback requires a resolvable configured owner.
6. RED: obsolete sender/poller settings are rejected if removed from the supported contract.
7. GREEN with the smallest production changes, then run focused webhook tests followed by complete backend/frontend checks.

## Common test-harness trap

Some handler constructors seed the dedicated integration for tests. Moving all setup exclusively into production `main` can make handler-level tests exercise a prototype/default inbox instead. Either keep harmless integration seeding in the handler while production startup performs checked/fail-fast setup, or make every test seed the integration explicitly. Never let production startup swallow setup errors merely for test convenience.
