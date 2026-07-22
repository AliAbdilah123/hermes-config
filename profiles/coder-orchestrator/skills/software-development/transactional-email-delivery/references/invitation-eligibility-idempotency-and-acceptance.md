# Invitation eligibility, idempotency, and acceptance

Use this checklist for program/workspace member invitations where email delivery alone is insufficient.

## Eligibility boundary

- Normalize email before every lookup and deduplication query.
- Resolve recipients through the canonical registered-account table, not a mirrored/profile table that may contain seeded or legacy users.
- Reject current active or pending membership.
- Reject banned membership at both invitation and join boundaries.
- Allow no membership row and explicit former-member states such as `inactive` or `left`.

## 24-hour idempotency

- Store an explicit UTC `expires_at` at creation.
- Before insertion, find a pending invitation for the same scope and normalized email with `expires_at > now`.
- Return the existing invitation without another provider call, audit event, or optimistic duplicate UI row.
- Serialize the lookup-and-create path or use a database constraint/transaction so concurrent requests cannot double-send.
- An expired prior invitation permits a new token and one new email.

## Delivery consistency

- Keep an injectable sender for endpoint tests.
- If successful delivery is required before an invitation exists, delete/roll back the new token when delivery fails.
- Provider errors must be sanitized; never expose response bodies, credentials, or authorization headers.
- Build links from the configured public web URL, include the token, and state the expiry in the message.

## Acceptance boundary

- The frontend must preserve the token from the emailed URL and submit it to the join endpoint.
- Validate token scope, recipient email, pending status, and expiry server-side.
- Consume the token atomically and reject reuse.
- Never let a generic rejoin path reactivate banned membership.

## Focused verification

Cover registered new users, former members, active/pending/banned users, unregistered addresses, normalized duplicates, one provider call within the validity window, renewal after expiry, recipient mismatch, expired/reused tokens, and banned reactivation.

When the workspace requires fresh verification evidence but has no canonical command, create an OS-safe temporary script with `mktemp /tmp/hermes-verify-<topic>-XXXXXX.sh`, run targeted tests plus the real build and local/public health probes, remove the script/artifacts, and report it explicitly as ad-hoc targeted verification—not as a green full suite. A health check proves deployment readiness, not actual email delivery; use a controlled recipient for live provider proof when authorized.
