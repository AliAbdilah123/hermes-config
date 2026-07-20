# Provider/config triage checklist

## Evidence

- Search for the user-visible error and mailer factory/selection function.
- Inspect service `Environment=` and `EnvironmentFile=` declarations, then the running process environment with values masked.
- Inventory configured provider variable names only (for example `RESEND_*`, `POSTMARK_*`, `SENDGRID_*`, `SMTP_*`).
- Confirm whether failed delivery removes, retains, or marks the invitation/reset token.

## Minimal HTTPS provider adapter

- JSON fields: sender, recipient list, subject, text or HTML.
- `Authorization: Bearer <key>` and `Content-Type: application/json`.
- Default provider URL in code; injectable URL/client only where needed for a focused local-server test.
- Accept all 2xx responses, close the body, and return a sanitized status error otherwise.
- Retain SMTP as fallback if it is already supported and configured.

## Verification ladder

1. Local provider-adapter test using an HTTP test server.
2. Endpoint test through the injected mailer.
3. Full application test suite.
4. Build the exact command package referenced by the service.
5. Restart and verify stable active state.
6. Submit one controlled real invitation and confirm provider acceptance/delivery.
7. Confirm the generated public invite link uses the correct scheme, host, and mount path.

## Secret handling

Do not print values, commit `.env`, or bake provider credentials into a binary. Reusing a host’s existing provider is acceptable only when authorized and configured in the target service’s protected environment.