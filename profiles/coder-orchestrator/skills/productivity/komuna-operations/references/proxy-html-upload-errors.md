# Proxy HTML Upload Errors (413 and Similar)

Use when a browser upload receives an HTTP error with an HTML body and the SPA incorrectly reports that the API is unavailable.

## Diagnosis

1. Preserve and inspect the HTTP status before parsing the body.
2. Compare public/proxied behavior with the direct upstream. An HTML error page often means the reverse proxy rejected the request before the application handler ran.
3. Inspect all effective request-size ceilings: CDN, Nginx, application body reader, multipart parser, and per-file validation.
4. Account for multipart overhead. For Komuna’s 5 MiB application file limit, set Nginx’s request ceiling slightly higher (for example 6 MiB), leaving the API as the authoritative validator.

## Minimal fix

- Retain application-side type and size validation.
- Set the proxy request limit above the file limit.
- In the frontend error parser, classify known statuses such as 413 before the generic “HTML means API unavailable” fallback.
- Show an actionable message with the accepted file limit.

Do not infer API availability from content type alone, and do not raise the proxy limit while removing application validation.

## Verification

- Add a frontend regression test with an HTML 413 response and assert the status-specific message.
- Run focused upload/API tests and a production typecheck/build.
- Run `nginx -t`, reload Nginx, and verify the public endpoint.
- When canonical verification detection is unavailable, create an OS-safe temporary script with `mktemp /tmp/hermes-verify-<topic>-XXXXXX.sh`, run focused checks, remove it, and report this explicitly as ad-hoc verification rather than claiming the full suite is green.
