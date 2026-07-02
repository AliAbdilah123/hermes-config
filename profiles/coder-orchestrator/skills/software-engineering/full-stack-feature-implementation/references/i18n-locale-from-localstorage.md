# Reading i18n locale from localStorage in library utilities

When a library utility (e.g., `formatPriceLabel`) needs the current language/locale
to format values, and the app uses `i18next-browser-languagedetector` which persists
to `localStorage` key `'language'`:

1. **Do NOT import i18n into the utility**: This adds a side-effect dependency that
   complicates tests (i18n initializes at import time, tries to detect browser language).

2. **Do NOT thread locale through every caller**: If 8+ components call the utility,
   changing all of them is high-diff and fragile.

3. **DO read from localStorage directly** with a safe fallback:

```ts
function getCurrentLocale(): string {
  if (typeof localStorage === 'undefined') return 'en'
  try {
    const stored = localStorage.getItem('language')
    if (stored === 'id' || stored === 'en') return stored
  } catch { /* private browsing */ }
  return 'en'
}
```

This works because:
- `i18n.changeLanguage()` fires `languageChanged` event synchronously
- `persistLanguagePreference` (listener) writes to localStorage synchronously
- React re-render (from `useTranslation`) happens after, so the util re-reads
  the updated value during render
- In tests, localStorage is available in jsdom; unset key falls back to default
- `typeof localStorage === 'undefined'` guards SSR/Node environments

Pitfall: This only works when i18n persists to localStorage (default with
`i18next-browser-languagedetector` + `caches: ['localStorage']`). If the app
switches to cookie-based or URL-based detection, update this accordingly.
