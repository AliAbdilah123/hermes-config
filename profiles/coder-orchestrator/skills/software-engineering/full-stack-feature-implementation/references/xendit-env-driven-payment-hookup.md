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
- **Explicitly set `callback_url`** in the invoice body to a public route that the backend serves. Without this, Xendit webhooks may never fire (especially in test/dev where the Xendit dashboard callback URL isn't configured). For subpath-deployed APIs, construct it as `{PUBLIC_BASE_URL}{API_BASE_PATH}/webhooks/xendit` — verify the base-path routing (nginx may strip to a non-base path; `callback_url` must hit a route registered under the API's mux prefix).
- `success_redirect_url` / `failure_redirect_url` can be built from `PUBLIC_BASE_URL`. For the failure URL, append `?payment=failed&purchaseId={id}` so the frontend can show a failed-payment card with a retry button.
- Persist gateway as `xendit` for real API calls and `mock_xendit` only for fallback mode.
- Store provider invoice id, invoice URL, and raw provider response; return the invoice URL as the payment link.

## Confirm/polling endpoint (handles webhook race)

Add a `POST /checkout/confirm` endpoint that polls the live Xendit invoice status
via `GET https://api.xendit.co/v2/invoices/{external_id}` with Basic auth.
This prevents the race where the redirect arrives before the webhook:

- Parse `Xendit invoice status` from the response. Treat `PAID`/`SETTLED`/`CAPTURED` as paid.
- On `paid` → issue vouchers (if not already issued). On `EXPIRED`/`FAILED` → mark purchase failed.
- Use a **shared `finishPurchase`** function called by both the webhook handler and the confirm endpoint, so status normalization and voucher issuance happens in one place.

## Go JSON-state API pitfalls (Komuna)

The Komuna Go API uses a `withState` wrapper that locks the mutex, calls `load()`,
runs a closure, calls `recalc()` / `save()`, then **auto-calls `jsonOut(w, res)`** with
the closure's return value. This means:

- **If `withState` is used for a handler that also calls `jsonOut`/`errOut` externally,
  you get a double HTTP response** (write-after-write panic or corrupted output).
- When the handler needs to write errors/per-request DTOs directly, skip `withState` and
  manually sequence `a.mu.Lock()` / `a.load()` / mutation / `s.recalc()` / `a.save()` / `a.mu.Unlock()`.
- The `finishPurchase` helper should also follow manual lock/load/save (no `withState`)
  so both the webhook and confirm caller control their own response bodies.

## Tests and verification

- Unit-test real Xendit request construction against an `httptest.Server`/fake HTTP server. Assert method/path, auth header presence, payload fields, and response parsing.
- Test `.env` loading with a temporary directory and `t.Setenv` to avoid leaking real credentials.
- Do not create a real live Xendit invoice during a routine smoke test unless the user explicitly asks for a live provider transaction. Report that the integration path is covered by fake-server tests and live service health checks.
- For deployed services, verify API health on the service port and public nginx route after restart.
