# Language accessibility i18n implementation

Use when implementing the approved SocialZen language/accessibility plan in the React/Vite frontend.

## Minimal implementation pattern

- Add a tiny app-local language provider instead of installing an i18n dependency for the first pass.
- Keep the storage key stable: `socialzen.language`.
- Default missing/invalid values to Indonesian (`id`); only explicit `en` selects English.
- Set `document.documentElement.lang` in the provider effect (`id` or `en`) when the selected language changes.
- Wrap the app under the existing providers in `src/main.tsx` so shell/navigation/settings can use the language hook.
- Start dictionaries with shared, high-traffic UI labels:
  - desktop/mobile nav
  - New Post / Logout
  - Settings title/subtitle/section labels
  - Settings → Accessibility language selector
  - loading text
- Add `accessibility` to `SETTINGS_SECTIONS`; the existing `/app/settings/:section` mobile route pattern will make it a mobile detail page automatically.

## Test/verification shape

- Add a focused unit test around language normalization/defaulting and `html lang` mapping. Keep it independent of React rendering when possible.
- Run:
  - `pnpm exec vitest run src/lib/language.test.ts`
  - `pnpm typecheck`
  - `pnpm build`
- Deploy the built `dist/` to `/var/www/html/projects/socialzen/` and verify:
  - public app URL returns 200
  - current public JS asset is `application/javascript`
  - deployed bundle contains markers such as `socialzen.language`, `Aksesibilitas`, and `Bahasa Indonesia`.

## Pitfalls

- Do not attempt to translate user-generated captions, provider/API error messages, or persisted backend data unless explicitly requested.
- Do not add backend schema/user-profile persistence for language unless cross-device sync is requested; localStorage is enough for the first pass.
- Because SocialZen is behind Cloudflare, verify the specific deployed JS asset, not only a successful local build.
