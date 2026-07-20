---
name: transactional-email-delivery
description: Diagnose, implement, test, and deploy application email delivery for invitations, password resets, and notifications across HTTPS providers and SMTP.
version: 1.0.0
metadata:
  hermes:
    tags: [email, invitations, smtp, transactional-email, debugging]
---

# Transactional Email Delivery

Use when an application’s invitation, password-reset, verification, or notification flow cannot send email, especially when it reports a generic unavailable/delivery error.

## Workflow

1. Find the exact error and trace the handler through mailer/provider selection.
2. Inspect the running service definition and effective environment source, with values masked. Source code and example env files do not prove runtime configuration.
3. Classify the failure: no provider configured, rejected credentials, rejected sender/domain/recipient, network failure, or application state rollback after delivery failure.
4. Look for an already-used transactional provider in the deployment environment. Reuse it intentionally rather than installing a local MTA or adding another provider without need. Never commit credentials or env files.
5. Preserve or introduce one small injectable mailer seam. Prefer deterministic selection: injected test mailer, configured HTTPS provider, configured SMTP fallback, then a clear unavailable error.
6. For simple HTTPS provider APIs, use the standard HTTP client: JSON payload, bearer authentication, response-body close, 2xx-only success, and sanitized errors.
7. Keep invitation/reset state consistent. If the product requires successful delivery before persistence, roll back/delete the token on send failure; otherwise explicitly model pending/failed delivery.

## Verification

Use a local HTTP test server to assert method, endpoint, auth header, content type, sender, recipient, subject, and generated URL. Keep an endpoint-level test through the injected mailer for token creation, URL generation, and rollback behavior.

Run the targeted test and full suite. Build the actual executable package used by the service (often `./cmd/<app>`, not repository root), restart after environment changes, and verify the process remains active. Finally exercise the real invitation flow with a controlled recipient when authorized; a health-page 200 does not prove email delivery.

See `references/provider-config-triage.md` for a compact provider/config diagnosis and deployment checklist.

## Pitfalls

- Do not treat missing SMTP variables as proof the product has no email provider; an HTTPS provider may already be configured elsewhere in the deployment.
- Do not copy secrets between projects into source control. If shared deployment credentials are intentionally reused, place them only in the target service’s protected runtime environment.
- Do not report success from tests plus a health check alone when the bug is delivery. Verify the real flow or clearly state that live delivery remains untested.
- Do not leak provider response bodies, authorization headers, or API keys in errors and logs.
