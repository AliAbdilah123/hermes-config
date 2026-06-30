# Frontend unknown-enum runtime crash

Use when a React/Vite SPA serves HTML and JS successfully, but the page is blank because React crashes during render with an error like `Cannot read properties of undefined (reading 'bg')`, `...stripe`, `...color`, etc.

## Pattern

A backend/API starts returning new enum-ish values that the frontend type union and lookup table do not know about. TypeScript may still pass because the DTO type is narrower than real runtime data, but production data can contain values like `green`/`blue` while the component only handles `warm`/`cool`/`ink`/`accent`.

Typical failing code:

```tsx
const tone = TONE_STYLES[item.imageTone ?? 'warm']
return <div style={{ background: tone.bg }} />
```

If `item.imageTone` is an unrecognized string, `tone` is `undefined` and render crashes before `#root` gets content.

## Investigation recipe

1. Fetch the public HTML and JS asset to confirm static serving is healthy.
2. Use a real browser/CDP/headless run to capture runtime exceptions; `curl` cannot see render crashes.
3. Query the deployed API response that feeds the blank page and inspect enum-ish fields used as object keys.
4. Search for lookup tables using the failing property names (`.bg`, `.stripe`, `.fg`, etc.).
5. Compare real API values against the frontend lookup keys/type unions.

## Fix pattern

Prefer fixing both layers when possible:

- Add a render-safe fallback at every lookup boundary:

```tsx
const tone = TONE_STYLES[item.imageTone ?? 'warm'] ?? TONE_STYLES.warm
```

- If the new values are legitimate product data, either add styles for them or broaden/normalize the DTO type deliberately.
- Apply the fallback to all similar image/theme lookup tables, not just the first crashing route.
- Add/update a regression test with a mocked API payload containing an unknown enum value.

## Verification

- `npm run build` / typecheck succeeds.
- Public deployed HTML references the new hashed bundle.
- Headless browser/CDP shows no `Runtime.exceptionThrown` and `#root` has non-zero rendered HTML/text.
- Verify a cache-busted public URL renders visible app text, not only HTTP 200.