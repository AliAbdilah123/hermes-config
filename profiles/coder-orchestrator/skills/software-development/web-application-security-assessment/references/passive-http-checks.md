# Passive HTTP/TLS Check Set

Use a small, bounded request set and replace `TARGET` with the authorized hostname. These commands are examples; omit checks that exceed scope.

## Baseline

```bash
curl -sS -D - -o /dev/null https://TARGET/
curl -sS -D - -o /dev/null http://TARGET/
```

Capture status, redirect location, security headers, cache policy, cookies, server disclosure, and framework disclosure.

## Certificate and protocol negotiation

```bash
openssl s_client -connect TARGET:443 -servername TARGET </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates -ext subjectAltName

for version in tls1 tls1_1 tls1_2 tls1_3; do
  printf '%s: ' "$version"
  timeout 10 openssl s_client -connect TARGET:443 -servername TARGET \
    -"$version" </dev/null 2>&1 \
    | grep -E 'Protocol *:|New, TLS|Cipher is|alert protocol version' | tail -1
done
```

A failed obsolete-protocol handshake is positive evidence. Preserve enough output to distinguish rejection from DNS/network failure.

## CORS

```bash
curl -sS -D - -o /dev/null \
  -H 'Origin: https://example.invalid' \
  https://TARGET/REPRESENTATIVE-ENDPOINT

curl -sS -i -X OPTIONS \
  -H 'Origin: https://example.invalid' \
  -H 'Access-Control-Request-Method: GET' \
  https://TARGET/REPRESENTATIVE-ENDPOINT
```

Record `Access-Control-Allow-Origin`, `Access-Control-Allow-Credentials`, allowed methods/headers, `Vary: Origin`, and status. Repeat only for representative API/auth endpoints already discovered from normal application use.

## Safe metadata checks

```bash
curl -sS -i https://TARGET/robots.txt
curl -sS -i https://TARGET/.well-known/security.txt
curl -sS -X TRACE -D - -o /dev/null https://TARGET/
```

A missing `security.txt` is informational. TRACE rejection is a positive control, not a comprehensive method audit.

## Cookie evidence

```bash
curl -sS -D - -o /dev/null https://TARGET/LEGITIMATE-UNAUTH-ENDPOINT
```

In reports, show cookie names and attributes but replace each value with `<redacted>`. Review `Secure`, `HttpOnly`, `SameSite`, `Path`, `Domain`, expiry, and cookie prefixes.

## Public asset review

1. Fetch the public HTML once.
2. Parse only linked `src`/`href` assets.
3. Download public JavaScript with request timeouts.
4. Search for API paths, absolute origins, public environment variables, browser storage, source-map comments, and credential-like material.
5. Inspect surrounding code before classifying any match.
6. Request only directly inferred `*.map` URLs; do not recursively guess asset names.

Common false positives include framework defaults such as `http://localhost:3000`, dependency error strings, generic `secret`/`token` identifiers, React's `dangerouslySetInnerHTML` implementation, and localStorage use internal to dependencies.

## Interpretation matrix

| Observation | Classification |
|---|---|
| Missing HSTS on HTTPS | Confirmed transport hardening gap |
| HTTP redirects to HTTPS | Positive control; does not negate missing HSTS |
| CSP includes `'unsafe-inline'` | Confirmed CSP weakness; not confirmed XSS |
| No ACAO for attacker origin | Positive evidence for tested endpoint only |
| Secure/HttpOnly/SameSite cookies | Positive control for observed cookies only |
| Public source map returns 200 | Review for sensitive source/config exposure |
| Public source map returns 404 | Positive evidence for tested map only |
| Version banners | Informational fingerprinting exposure |
| Missing COOP/CORP/COEP | Optional defense-in-depth unless app threat model requires isolation |
| Auth/IDOR/rate-limit concern without account tests | Unverified risk |

## Minimal evidence record

For each request retain:

- UTC timestamp
- exact URL and method
- relevant request headers
- response status and relevant headers
- short redacted body snippet when needed
- exact reproduction command

Avoid publishing full HTML or minified bundles when a short excerpt proves the point.