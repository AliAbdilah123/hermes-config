# Language / Accessibility i18n planning

Use this when SocialZen needs app-language support or a language switcher.

## Product shape

- Default language should be Indonesian (`id-ID`) unless a user has explicitly chosen another language.
- Put the language switcher under **Settings → Accessibility**.
- Support at least Indonesian ↔ English switching.
- Persist the choice client-side (`localStorage` is enough unless the user asks for cross-device sync).
- Update `document.documentElement.lang` to `id` or `en` so screen readers/browser translation hints match the UI.

## Minimal implementation direction

- Prefer a tiny in-app translation helper over adding an i18n dependency for the first pass: active language state, `setLanguage`, and `t(key)`.
- Add `accessibility` to `SETTINGS_SECTIONS` in `SettingsPage.tsx`; mobile settings already routes sections through `/app/settings/:section`, so the new section should automatically work if added to the section list and render switch.
- Start with shared navigation/settings labels and high-traffic screens, then expand dictionaries screen-by-screen.
- Keep user-generated content, captions, API/provider error messages, and stored data unchanged unless explicitly requested.
- Use active locale for date/number formatting where the app already formats values; keep IDR currency formatting as Rupiah.

## Review artifact expectation

Because the user prefers review docs/plans before implementation, publish a styled responsive HTML plan first for language/i18n changes. Use the SocialZen PRD route:

`https://socialzen.ahsanworks.com/prd/socialzen/<slug>.html`

Verify both local `/prd/socialzen/<slug>.html` and the public Cloudflare URL return 200 before reporting the plan link.
