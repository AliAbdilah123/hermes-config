# Webhook token env alias and live verification

Use when webhook verification returns `403` even though an operator says the token exists in the service `.env`.

## Diagnosis

1. Read the verification handler and trace its configured field through startup wiring and the config loader.
2. Compare the exact env key consumed by code with the key present in the effective runtime env file. Do not print token values; report only presence, length, or a redacted hash.
3. Inspect systemd `ExecStart`, `WorkingDirectory`, and the `-env`/`EnvironmentFile` path. `/proc/<pid>/environ` may omit values when the application parses an env file itself rather than receiving exported variables.
4. Reproduce at both boundaries: direct local upstream and the exact public URL through nginx/CDN.

## Minimal compatibility fix

When a deployed accepted key differs from the canonical key, map both to the same internal field at the config-loader boundary, with canonical precedence:

```go
WebhookVerifyToken: firstNonEmpty(values["CANONICAL_WEBHOOK_VERIFY_TOKEN"], values["LEGACY_OR_PROVIDER_SPECIFIC_WEBHOOK_TOKEN"])
```

Keep the alias in the supported-key allowlist. Add focused tests for canonical and alias loading; test precedence if both may coexist. Do not duplicate alias logic in the HTTP handler.

## Deployment and verification

1. Run focused config and webhook-handler tests.
2. Build and install the exact binary named by systemd.
3. Restart, then inspect fresh status/logs for the actual listener; do not assume a familiar port.
4. Build the verification request from the effective env file without displaying the token. For Meta, send exact `hub.mode`, `hub.verify_token`, and a non-empty `hub.challenge`.
5. Require both local upstream and public endpoint to return `200` and echo the challenge exactly.
6. If local succeeds but public fails, probe origin with `curl --resolve`, then retry the public edge to distinguish origin/nginx behavior from transient CDN state.

## Pitfalls

- Opening a URL in a browser sends GET; it does not test event POST delivery.
- Verification GET and event POST are separate contracts. Do not offer a “valid POST” when only GET is registered.
- Leading punctuation or whitespace is part of the token and breaks exact comparison.
- `systemctl is-active` proves lifecycle, not readiness or webhook behavior.
- Never expose webhook tokens in output, logs, commits, or final responses.
