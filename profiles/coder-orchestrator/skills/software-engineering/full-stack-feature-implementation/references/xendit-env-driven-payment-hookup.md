# Xendit env-driven payment hookup notes

Use when an existing Go/API project has mock Xendit billing and the user adds a project-level `.env` with Xendit credentials.

## Durable pattern

- Do not print or read secret values. Inspect only key names if needed.
- Support both common secret names when wiring config: `XENDIT_SECRET` and `XENDIT_SECRET_KEY`.
- Add a small `.env` loader only if the runtime does not already load project env. Search current/parent dirs as needed, but let real process env override `.env` values.
- For deployed systemd services, code-level `.env` loading may not find a project dir if `WorkingDirectory` is under `/var/lib/...`; add `EnvironmentFile=/path/to/project/.env` to the service instead of copying secrets into the unit file.
- Restart with `systemctl daemon-reload` + service restart, then verify `systemctl show <service> -p EnvironmentFiles -p ActiveState` without printing environment contents.

## Xendit invoice adapter

- Keep mock fallback for local development only when no Xendit secret is configured.
- Real checkout should create a Xendit invoice via `POST {XENDIT_API_BASE:-https://api.xendit.co}/v2/invoices`.
- Authenticate with HTTP Basic auth using the secret as username and an empty password.
- Minimum invoice payload: `external_id`, `amount`, `currency`, `description`, and useful metadata (`tenant_id`, `plan_id`, billing interval).
- Optional redirects can be built from `PUBLIC_BASE_URL` as `success_redirect_url` / `failure_redirect_url`.
- Persist gateway as `xendit` for real API calls and `mock_xendit` only for fallback mode.
- Store provider invoice id, invoice URL, and raw provider response; return the invoice URL as the payment link.

## Tests and verification

- Unit-test real Xendit request construction against an `httptest.Server`/fake HTTP server. Assert method/path, auth header presence, payload fields, and response parsing.
- Test `.env` loading with a temporary directory and `t.Setenv` to avoid leaking real credentials.
- Do not create a real live Xendit invoice during a routine smoke test unless the user explicitly asks for a live provider transaction. Report that the integration path is covered by fake-server tests and live service health checks.
- For deployed services, verify API health on the service port and public nginx route after restart.
