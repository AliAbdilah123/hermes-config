# Public E2E route and selector drift

Use this when a deployed change passes local tests/builds but the repository's public E2E fails before reaching the changed behavior.

## Separate harness drift from product failure

1. Read the E2E script before interpreting its failure.
2. Compare its default base URL with the project's current public URL/metadata. If they differ, rerun with the script's supported URL override rather than editing product code.
3. If an accessible control was added near a form field, check for selector ambiguity. For example, a password input labeled `Password` plus a `Show password` button can make `getByLabel('Password')` non-unique. Prefer a role-constrained selector such as `getByRole('textbox', {name: 'Password'})`.
4. Patch the reusable E2E harness when its selector is genuinely stale, then rerun it. Do not weaken product accessibility to preserve a broad test selector.
5. If the broad suite then fails on unrelated stale fixture labels or tenant names, run a minimal public browser probe for the exact acceptance path. Record both facts: scoped acceptance passed; broader suite remains blocked by unrelated harness/fixture drift.
6. In an ad-hoc browser probe, apply the canonical suite's expected-error exclusions (for example, the initial unauthenticated session request returning 401). Otherwise a valid authentication bootstrap can be misreported as a browser regression.
7. After restarting a service, do not treat `systemctl is-active` as readiness. Poll the local health endpoint with a bounded retry, then verify the public health endpoint and deployed asset fingerprint before browser acceptance checks.

## Logout/navigation probe

For logout route-reset changes, verify all of the following in a fresh public browser context:

- sign in from the public root;
- navigate to a non-root protected route;
- activate the real Sign out control;
- wait for the login heading;
- assert the browser pathname is exactly `/`;
- where required, sign in as another role and confirm role-based root routing rather than inherited history.

A login screen alone is insufficient evidence: the old protected pathname can remain while unauthenticated content renders.
