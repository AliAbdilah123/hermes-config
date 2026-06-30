# Frontend theme color-scheme and dark-mode mismatch debugging

Use this when a mobile browser appears to show a darkened UI while the app state says light mode, or when switching to dark mode makes the UI even darker / text unreadable.

## Reproduction / evidence checklist

1. Inspect the theme state source:
   - localStorage key(s) such as `theme`
   - document root class such as `.dark`
   - any `prefers-color-scheme` logic
2. Inspect CSS tokens used by most UI text and surfaces. In Tailwind/Vite apps with custom CSS variables, search for tokens such as `--ink`, `--ink-2`, `--bg`, `--line`, `--foreground`, `--background`.
3. Verify whether dark mode overrides every semantic text token. A common bug is `.dark { --foreground: light; --ink: dark; }` while components actually use `var(--ink)`, making text unreadable.
4. Check browser color-scheme hints:
   - `color-scheme: light` on `:root`
   - `color-scheme: dark` on `.dark`
   - `<meta name="color-scheme" content="light dark" />`
   These reduce mobile browser auto-darkening / form-control mismatch issues.
5. Check brand/logo tokens separately from text tokens. Logos should not depend on `--ink`/`--foreground` if those swap for readability.

## Fix pattern

- Keep the app's default theme explicit (`light`) unless the product intentionally follows system preference.
- In `.dark`, make semantic text tokens light and readable, not just shadcn/Tailwind `--foreground`:
  - `--ink`: primary readable text
  - `--ink-2`: secondary readable text
  - `--ink-3`: muted but still visible text
  - `--line` / `--line-2`: visible but subtle borders
  - `--bg`: clean dark surface
- Add stable brand tokens, for example:
  - `--brand-mark-bg`
  - `--brand-mark-fg`
  Then update logo components to use those tokens instead of theme text tokens.
- Avoid active states like `bg-[var(--ink)] text-white` when `--ink` changes to light in dark mode. Use semantic primary tokens or dedicated nav-active tokens.

## Regression test idea

A lightweight CSS-token test can read `globals.css` and assert that `.dark` defines readable `--ink*` values and that stable brand mark tokens exist. This catches future regressions without needing visual browser automation.

## Deployment verification

After building and publishing the frontend, fetch the public HTML and hashed CSS asset. Confirm the deployed CSS contains the intended tokens, e.g. `--ink:#f7f2ff`, `--brand-mark-bg:#1a1625`, and `color-scheme:dark`.
