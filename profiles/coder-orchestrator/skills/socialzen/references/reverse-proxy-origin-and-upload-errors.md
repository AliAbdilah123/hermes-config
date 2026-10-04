# Reverse-proxy origin validation and upload errors

Use when browser reads succeed but cookie-authenticated writes return `403 FORBIDDEN_ORIGIN`, especially on an HTTPS dev domain behind local nginx.

## Strict TDD sequence

1. Add a backend regression request with:
   - `Origin: https://<public-host>`
   - internal `r.Host`
   - `X-Forwarded-Host: <public-host>`
   - `X-Forwarded-Proto: https`
   - loopback `RemoteAddr`
2. Run only that test and confirm it fails because the public origin is rejected.
3. Add a companion security test proving a non-loopback peer cannot spoof matching forwarded headers.
4. Make `sameOriginRequest` consult forwarded host/proto only when the direct peer is trusted (for SocialZen's local nginx topology, loopback). Continue comparing parsed scheme + host; do not accept arbitrary forwarded values or loosen the session-cookie CSRF gate.
5. Add a frontend test whose XHR returns an HTML/non-JSON error body and confirm the existing unconditional `JSON.parse` fails.
6. Parse upload responses defensively. On non-2xx, always reject an `ApiError` using status/statusText fallbacks. Handle `onerror`, `onabort`, and `ontimeout` with stable `ApiError` codes.

## Proxy configuration

The application fix is insufficient unless nginx supplies the public request identity. In each API proxy location, set:

```nginx
proxy_set_header Host $host;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Proto https;
```

Use `$scheme` only when nginx itself receives the browser's HTTPS connection. If TLS is terminated by an upstream proxy and nginx receives HTTP, `$scheme` will incorrectly report `http`; use a trusted upstream's forwarded protocol or the known HTTPS virtual-host value. Validate with `nginx -t`, reload nginx, and then exercise a harmless public cookie-authenticated POST. A controlled auth/session response or success proves origin validation was passed; `FORBIDDEN_ORIGIN` means it was not.

## Focused verification

- Go: `go test . -run 'TestSameOriginRequest' -count=1`
- Frontend: `pnpm exec vitest run src/lib/api.test.ts`

Do not use `pnpm test -- <file>` here: the current script/config may still collect the whole frontend suite. Then run backend build, frontend typecheck/build, deploy both artifacts, restart the service safely, and verify public health plus the write path.

## Deployment and evidence pitfalls

- Persist the nginx change in the server-owned configuration/workflow; a source-only commit does not deploy proxy headers.
- A public health `200` proves reads only. Include a non-destructive public POST with the exact public `Origin`.
- Authenticated upload/disconnect E2E requires a safe test session/account. Never disconnect a real provider connection merely to prove the CSRF fix unless reconnection is known safe.
- Preserve runtime SQLite and unrelated dirty artifacts. Stage only task-owned source/test paths or hunks.
- If the full suite has unrelated failures, report focused green evidence and the exact full-suite failures separately; do not call the full suite green.
