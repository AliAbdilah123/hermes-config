# Public legal pages for SocialZen

Use this when adding or revising Terms, Privacy, Security, or Data Deletion pages.

## Implementation shape

- Add unauthenticated React routes for `/terms`, `/privacy`, `/security`, and `/data-deletion` inside the existing `BrowserRouter`; the production basename supplies `/projects/socialzen` externally.
- Reuse one semantic legal-document shell and one data/content file rather than four duplicated page layouts.
- Include a visible `Last Updated`, responsive table of contents, cross-links, landing footer links, signup consent links, document title, meta description, robots, Open Graph fields, and canonical URL.
- Keep Data Deletion informational. Point users to the authenticated Settings → Danger Zone flow; do not place a deletion action on the public page.
- Reuse existing theme tokens, `ThemeToggle`, button variants, and landing footer. Do not add a dependency.

## Legal-content accuracy gate

Before publishing, verify every operational claim against deployed code/config. In particular:

- actual company/operator identity and governing law;
- support/contact address;
- active infrastructure and subprocessors (do not claim Neon or another provider merely because it appeared as an example if production uses SQLite or a different service);
- OAuth scopes currently requested;
- password/session/token protections actually implemented;
- export expiry, deletion recovery window, permanent-deletion schedule, and retained audit/tombstone periods;
- paid-plan renewal, refund, payment-provider, and cancellation behavior.

If a required legal fact is unknown, use accurate qualified wording or ask for confirmation. Do not invent a liability cap, office location, processor, retention period, or security control. Legal copy must describe the product as it exists, not a desired architecture.

## Provider-neutral wording scope

- A request to remove named infrastructure vendors from the Privacy Policy may expose the same names on Security because all public legal documents share one content module. Audit the rendered Privacy and Security pages before finishing, especially “Infrastructure and availability” and “Provider and data lifecycle controls.”
- Preserve legal meaning by replacing vendor names with functional categories such as infrastructure, edge delivery, network protection, managed data services, email delivery, product analytics, identity, social-platform, and payment providers. Do not remove the underlying disclosure about subprocessors, transfers, controls, or outages.
- Keep tests document-scoped: assert retired names are absent from each revised page’s rendered DOM. A shared JavaScript chunk is not proof of a page-level disclosure because it contains content for multiple legal routes.

## Verification

1. Run the focused legal-page render test, frontend typecheck, and a fresh `pnpm run build` before calling the change verified. If `pnpm` is not directly on `PATH` but npm is available, `npm exec --yes pnpm -- run build` preserves the requested pnpm build path; do not treat an earlier equivalent build as fresh evidence when the verification gate asks again.
2. For provider-neutral legal revisions, render every revised document and assert its DOM contains the neutral category and omits the retired vendor names. Do not assert that the shared `LegalPages-*.js` bundle omits those names unless every document in that chunk was revised.
3. Deploy the clean `dist/` to `/var/www/html/projects/socialzen/` and verify each prefixed public route returns `200 text/html`.
4. Locate the built `LegalPages-*.js`, verify `Content-Type: application/javascript`, and grep a distinctive marker from the revised document.
5. Check the four production URLs through the public endpoint.
6. Capture at least one desktop and one narrow mobile screenshot. Confirm no horizontal overflow, clipped navigation, unreadable secondary text, or broken footer layout.
7. Commit and push only the feature files; leave unrelated untracked plans/docs untouched.

A lightweight screenshot fallback is an ephemeral Playwright CLI invocation using the already-available Chromium browser. Treat screenshot analysis as supplementary to route, bundle, test, and content-accuracy checks.