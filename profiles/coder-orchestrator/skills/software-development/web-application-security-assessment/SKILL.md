---
name: web-application-security-assessment
description: Use when conducting an authorized, non-destructive vulnerability assessment of a public web application through passive reconnaissance and low-impact HTTP, TLS, browser, cookie, CORS, and public-client checks. Produces evidence-backed findings that clearly separate confirmed weaknesses from unverified risks.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [security, web, assessment, tls, headers, cors, cookies]
    related_skills: [dogfood]
---

# Web Application Security Assessment

## Overview

Assess an authorized web target without brute force, aggressive fuzzing, account exploitation, state changes, or availability testing. Prefer a small number of deliberate requests and preserve exact evidence. A missing defense-in-depth control is not automatically an exploitable vulnerability.

For the tested passive probe set and interpretation notes, read `references/passive-http-checks.md`.

## When to Use

- The user requests passive reconnaissance or a safe vulnerability review of a URL.
- The scope emphasizes headers, TLS, cookies, CORS, public JavaScript, or exposed configuration.
- The assessment must distinguish confirmed findings from risks requiring authentication or source review.

Do not use this workflow to justify credential attacks, broad directory enumeration, destructive payloads, load testing, or bypass attempts outside explicit authorization.

## Workflow

### 1. Fix scope and safety boundaries

Record the exact host, permitted techniques, forbidden actions, and whether accounts/test data are available. Do not silently expand to sibling hosts or ports. This step is complete when every planned request is clearly within scope and low impact.

### 2. Capture baseline transport evidence

Collect DNS resolution, HTTP-to-HTTPS behavior, HTTPS response headers, certificate subject/SAN/issuer/dates, and negotiated TLS versions. Use timeouts and individual requests rather than scanners by default.

Interpretation rules:

- A redirect to HTTPS does not replace HSTS.
- Report TLS versions only from actual handshakes; do not infer cipher quality from a certificate.
- Certificate transparency, CAA, OCSP stapling, and preload status are separate controls.
- Record the observation time because certificates and headers change.

This step is complete when the report can reproduce each transport claim with a command and observed output.

### 3. Inspect HTTP defenses

Check the main page and representative error/auth/API responses for:

- `Strict-Transport-Security`
- `Content-Security-Policy`
- `X-Content-Type-Options`
- `X-Frame-Options` or CSP `frame-ancestors`
- `Referrer-Policy`
- `Permissions-Policy`
- `Cross-Origin-Opener-Policy`, `Cross-Origin-Resource-Policy`, and when relevant COEP
- version banners and framework disclosure
- cache behavior on sensitive responses

Do not inflate severity. Missing HSTS is a confirmed hardening gap; it is not proof of session compromise. CSP `'unsafe-inline'` weakens containment; it is not proof of XSS.

### 4. Check CORS deliberately

Send both a simple request with a foreign `Origin` and an OPTIONS preflight to representative public/API endpoints. Record `Access-Control-*`, `Vary`, status, and credential behavior.

Never conclude “CORS is secure” from the homepage alone. Scope the statement to the tested endpoints. Absence of `Access-Control-Allow-Origin` for an attacker origin is positive evidence, not proof about every endpoint.

### 5. Inspect cookie attributes safely

Use unauthenticated endpoints that legitimately set cookies. Record names and attributes without publishing live token values. Check:

- `Secure`
- `HttpOnly`
- `SameSite`
- host-only behavior and `__Host-` / `__Secure-` prefixes
- `Domain`, `Path`, and expiry where present

A CSRF token returned in a dedicated CSRF response may be normal framework behavior; evaluate the full token/cookie validation design before calling it exposure.

### 6. Review public client assets

Download only assets linked by public pages. Extract routes, API paths, public configuration, third-party origins, storage use, and source-map references. Search for credentials and keys, then validate context before reporting: framework strings such as `localhost`, `secret`, `token`, or `dangerouslySetInnerHTML` are frequently library code and not findings.

Request only directly referenced source-map URLs. A `404` is useful negative evidence. Do not recursively enumerate chunk namespaces or hidden paths.

### 7. Verify low-impact method and metadata behavior

When useful, check `TRACE`, `robots.txt`, and `/.well-known/security.txt`. Treat missing `security.txt` and version banners as informational unless context raises impact. Do not probe unsafe methods with state-changing bodies.

### 8. Classify results

Use three explicit buckets:

1. **Confirmed findings** — directly observed weakness with bounded impact.
2. **Positive controls** — protections verified on named endpoints.
3. **Unverified risks** — plausible issues needing accounts, source, test data, or invasive actions.

For each confirmed finding include severity, evidence, impact without exaggeration, reproduction command, and remediation. If no high-severity issue was found, say so directly without implying the application is fully secure.

## Reporting Format

Keep the deliverable concise and operational:

```text
Assessment outcome
Confirmed findings
  [Severity] Title
  Evidence: URL/header/snippet
  Impact: bounded claim
  Reproduce: exact command
  Remediation: concrete setting/change
Positive controls verified
Unverified risks / coverage limits
```

Redact cookie values, CSRF tokens, session identifiers, and any accidental secret. Include exact URLs and response header names. Mention tooling limitations only when they materially reduced coverage; never convert a transient setup failure into a durable claim about a tool.

## Common Pitfalls

1. **Calling every missing header a vulnerability.** Separate exploitable defects from hardening gaps and optional isolation controls.
2. **Treating CSP keywords as confirmed XSS.** `'unsafe-inline'` increases impact if injection exists; injection still needs evidence.
3. **Dumping live cookie/token values into the report.** Preserve attributes, redact values.
4. **Searching minified bundles without context.** Validate whether a hit belongs to application code, runtime code, or a dependency.
5. **Overclaiming coverage.** Unauthenticated passive checks cannot establish IDOR, rate limiting, stored XSS, business-logic integrity, or authorization correctness.
6. **Using broad scanners by default.** Prefer narrow native HTTP/TLS commands; add tooling only when it materially improves authorized coverage.
7. **Reporting stale facts.** Record that results are point-in-time observations.

## Verification Checklist

- [ ] Scope stayed on the authorized host and respected all prohibited actions.
- [ ] Every confirmed finding has direct evidence and a reproduction command.
- [ ] Severity reflects demonstrated impact rather than hypothetical impact.
- [ ] CORS claims name the tested endpoints and origins.
- [ ] Cookie values and tokens are redacted.
- [ ] Client-side matches were context-validated.
- [ ] Positive controls and unverified risks are separate from findings.
- [ ] Coverage limits are explicit.
- [ ] Remediations are concrete and compatibility caveats are noted.
