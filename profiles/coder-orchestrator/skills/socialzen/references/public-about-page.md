# Public About page for SocialZen

Use this when adding or revising SocialZen’s public company/product-description page.

## Implementation shape

- Add an unauthenticated React route at `/about`; production’s `BrowserRouter` basename exposes it as `/projects/socialzen/about`.
- Reuse the existing public header conventions, theme tokens, buttons, `ThemeToggle`, and `LandingFooter`; do not add a dependency or create a parallel design system.
- Wire the existing footer `About` item to `/about` rather than leaving it as `#`.
- Describe the product as it exists: supported Facebook, Instagram, and Threads connections; drafts and media; scheduling/publishing; supported comments/replies; analytics; subscriptions; export; and account deletion.
- Explain target users and product principles such as calm workflow, user control, security, and privacy.
- Include useful CTAs to signup, Security, and Privacy.
- Add page-specific title, description, robots, Open Graph metadata, and canonical URL. Build canonical URLs from `window.location.origin` plus the router-visible path; verify the production basename behavior rather than hardcoding the public prefix into React links.

## Accuracy and copy guardrails

- Do not invent founders, team biographies, office locations, company history, customer counts, awards, uptime, certifications, or performance claims.
- Qualify third-party behavior: comments, replies, publishing, and analytics work only where the connected platform/account supports them.
- Keep public branding consistently `SocialZen`; remove leftover prototype branding or location/version slogans when touching the shared footer.
- Prefer explicit labels such as `Privacy Policy` over awkward shorthand such as `Read privacy`.
- Keep CTA wording reasonably consistent across header, hero, and closing panel.

## Verification

1. Add one focused render test covering the H1, core capability copy, signup/security/privacy links, footer About link, title, meta description, and canonical URL.
2. Run the focused test, frontend typecheck, and production build.
3. Deploy a clean `dist/` to `/var/www/html/projects/socialzen/`.
4. Verify `/projects/socialzen/about` returns `200 text/html`, the built `AboutPage-*.js` returns `application/javascript`, and the bundle contains a distinctive About-page marker.
5. Capture a narrow full-page production screenshot. Check header controls, CTA wrapping, cards, footer stacking, contrast, clipping, and horizontal overflow.
6. Commit and push only the feature files; preserve unrelated untracked plans/docs.
