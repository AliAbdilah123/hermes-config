# Non-destructive Live Security Assessment

Use this reference when a user requests a vulnerability review of a public web application plus a styled report.

## Authorization and safety boundary

- State that testing is non-destructive unless the user explicitly authorizes a broader scope.
- Prefer passive reconnaissance and low-impact protocol checks.
- Do not brute-force credentials, stress availability, create accounts unnecessarily, mutate application data, enumerate sensitive datastore contents, or attempt persistence.
- If a severe exposure is confirmed, stop at the minimum evidence needed to prove impact. Do not escalate merely to demonstrate that escalation is possible.
- Record what was tested and what was intentionally excluded.

## Parallel evidence tracks

Run independent tracks where possible:

1. **Web edge:** HTTP-to-HTTPS behavior, TLS certificate and supported protocol versions, security headers, cookie attributes, CORS, cache policy, framework/server disclosure, common metadata files, and source-map exposure.
2. **Application surface:** public routes, auth/session bootstrap, unauthenticated admin behavior, client bundles, API paths, and safe method handling. Treat unusual status codes as leads, not vulnerabilities, until impact is demonstrated.
3. **Network exposure:** DNS and a small, justified list of common service ports. When a service answers, use only a protocol-native, non-mutating identification command.
4. **Independent review:** ask a separate audit track to challenge severity and identify missed controls.

## Minimum-evidence rule for exposed datastores

For a publicly reachable datastore such as Redis:

- A protocol response to a harmless command (for example, Redis `PING`) proves reachability.
- A non-mutating identity or server-info command may establish authentication state and listener configuration.
- Stop before key listing, value reads, writes, configuration changes, module/filesystem operations, or exploit attempts.
- Report the finding as confirmed exposure, but make downstream consequences conditional unless directly demonstrated.
- Recommend immediate network containment, private binding, least-privilege authentication/ACLs, credential rotation, log preservation, compromise review, and an external reachability retest.

## Classification discipline

- Separate **confirmed vulnerability**, **confirmed hardening gap**, and **untested/conditional risk**.
- Missing HSTS is a transport-policy gap; explain first-visit downgrade risk without overstating exploitation.
- CSP containing `script-src 'unsafe-inline'` is a hardening weakness, not confirmed XSS absent an injection point.
- Product/framework banners are usually low severity; patching matters more than obscurity.
- Record positive controls too (modern TLS, framing protection, secure cookies, restrictive CORS, blocked metadata paths). This prevents a sensationalized report.

## Styled report requirements

Include:

- concise executive summary and immediate containment callout;
- severity counts and overall risk;
- exact reproducible evidence with timestamps/target identity;
- impact phrased to match demonstrated evidence;
- remediation and external retest criteria;
- tested/not-tested boundary;
- positive controls;
- staged delivery order;
- responsive layout, accessible theme toggle, focus styles, reduced-motion support, and mobile-safe evidence blocks.

Never publish secrets, sensitive values, authentication material, or exploit payloads in the report.

## Verification

After the final edit:

1. Run deterministic checks for viewport, theme persistence, breakpoints, reduced motion, expected finding IDs/count, and required scope language.
2. Publish with least privileges and verify local HTTP 200.
3. Verify the public URL with a cache-busting query and assert that distinctive final content is present—not merely that the endpoint returns 200.
4. Report browser-rendering limitations honestly; HTTP/content checks do not prove visual quality.