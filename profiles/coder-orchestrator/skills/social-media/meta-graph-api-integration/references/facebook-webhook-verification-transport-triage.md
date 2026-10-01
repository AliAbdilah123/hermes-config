# Facebook webhook verification transport triage

Use when Meta reports **“The callback URL or verify token couldn't be validated”** for Facebook/Messenger.

## Required contract

Probe the exact callback without following redirects:

```text
GET <callback>?hub.mode=subscribe&hub.verify_token=<runtime-token>&hub.challenge=TEST123
```

Success requires all of:

```text
HTTP 200
Content-Type: text/plain
Body bytes: TEST123
No redirect
```

A bare callback request is not a valid verification test.

## Read-only isolation sequence

1. Identify the exact callback URL entered in Meta. Do not substitute a similar Instagram callback or a path-prefixed deployment URL.
2. Identify the service and secret source actually used by its running process (`systemctl cat`, `ExecStart`, env-file argument, listener). Report only token presence/length; never print it. If the application receives an `-env`/config-file argument and loads that file itself, `/proc/<pid>/environ` may correctly show no token; inspect the named file's key presence/length and the loader code instead of concluding configuration is absent.
3. Verify that the expected provider-specific variable exists. An Instagram webhook token does **not** establish that a Facebook verify token is configured. When the user supplies a screenshot containing a token, compare it to the configured value locally and report only `matches=true/false` plus lengths—never repeat either value. Probe direct and public callbacks with that supplied value to prove or disprove a mismatch.
4. Confirm the deployed binary/source registers the exact Facebook GET route. A working Instagram route is not evidence that the Facebook route exists.
5. Probe three boundaries using the same redacted/configured token and challenge:
   - public callback, redirects disabled;
   - origin Nginx vhost with preserved Host/SNI;
   - direct Go/upstream listener using its internal route.
6. Compare status, `Content-Type`, body bytes, and `Location` at every boundary.
7. Correlate the probe with Nginx access logs and service logs to determine whether Meta/public traffic reached Nginx and then the Go handler.

## Failure classification

- Public redirect (`301/302/307/308`): callback URL/canonicalization or edge/Nginx failure.
- Public and origin Nginx `404 text/html`, direct Go route works: missing/wrong Nginx location or proxy path rewrite.
- Public and origin Nginx `404 text/html`, direct Go also `404 text/plain`: both public routing and application route are absent; adding only a proxy cannot complete verification.
- Public reaches Go and returns `403`: route exists; investigate runtime token source, mode, query decoding, or empty challenge.
- Public returns `200` with JSON/HTML/wrapped challenge: response contract failure in handler/proxy transformation.
- No matching access-log entry: DNS/TLS/CDN/firewall or wrong callback hostname/path before Nginx.

## Security and evidence handling

Nginx access logs commonly record the full query string, including `hub.verify_token`. Never paste matching raw log lines into chat or reports. Extract only timestamp, method/path with query redacted, status, user agent, and request count. Likewise, do not derive or display a token from screenshots, session history, process arguments, or logs.

Meta may append underscore aliases such as `hub_mode`, `hub_challenge`, and `hub_verify_token` in addition to canonical dotted keys. Handlers should rely on the documented dotted keys; note aliases only as observed request evidence.

## Reporting format

Report:

- exact callback URL (without query secret);
- actual public status, content type, body, and redirects;
- whether Nginx received it;
- whether the Go service received/implements the exact route;
- the first failing component;
- no changes made when diagnosis-only was requested.

Do not label this a token mismatch unless a provider-specific handler actually received the request and rejected the comparison.
