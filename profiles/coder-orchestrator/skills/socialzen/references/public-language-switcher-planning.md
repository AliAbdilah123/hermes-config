# Public global language switcher planning

Use this when SocialZen needs language selection across unauthenticated marketing/legal pages rather than only authenticated Settings.

## Product boundary

- Follow the requested placement exactly: in the public top-right navigation, after the theme toggle and before Login/Get Started.
- Reuse one `PublicLanguageSwitcher` in both `LandingNav` and the shared public/legal-page shell so Landing, Terms, Privacy, Security, and Data Deletion cannot drift.
- Support English and Bahasa Indonesia with one browser-wide `localStorage` preference.
- Changing language must update the mounted page immediately through shared React state/context and update `document.documentElement.lang`.
- Preserve the current public-site language as the default unless the request explicitly changes the default. Do not inherit the authenticated Settings default blindly.
- Translate all visible product-owned copy on every page named in the request. Leave user content and provider/API text unchanged unless requested.

## Minimal implementation

1. Extend the existing lightweight language helper/provider; do not add an i18n dependency for two locales.
2. Use one shared dictionary boundary and one reusable dropdown with an accessible name and keyboard behavior.
3. Keep the selector responsive within the existing header; do not displace or wrap authentication actions unexpectedly.
4. Test persistence, immediate rerender, `<html lang>`, and both public navigation hosts.
5. Run focused tests, typecheck, and a fresh production build; then visually check desktop/mobile in both themes before deployment.

## Plan-first correction

An older Settings → Accessibility language plan does not satisfy a request for a global public-navigation switcher. Produce a new scoped review artifact that explicitly names placement, required routes, default-language behavior, and what remains outside scope. Stop after publishing the review unless implementation was already approved or the user explicitly requested skipping review.
