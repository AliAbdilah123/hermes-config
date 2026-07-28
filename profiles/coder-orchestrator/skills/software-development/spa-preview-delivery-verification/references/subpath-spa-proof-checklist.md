# Subpath SPA proof checklist

## Build identity

- [ ] Public base is exactly `/previews/<slug>/`.
- [ ] Runtime router basename matches that path.
- [ ] API base is explicit and does not resolve to SPA HTML.
- [ ] Generated asset URLs include the preview prefix.

## Server identity

- [ ] Explicit preview location has priority over production fallback.
- [ ] Preview `try_files` fallback points to preview `index.html`.
- [ ] Configuration validates and reload succeeds.
- [ ] Production files/hashes are unchanged.

## Transport proof

Record URL, status, and content type for:

| Probe | Expected |
|---|---|
| Preview root | 200 HTML from preview |
| Hashed JS | 200 JavaScript MIME |
| Hashed CSS | 200 CSS MIME |
| SPA deep route | 200 preview HTML |
| API endpoint | JSON/auth response, never HTML |

## Browser proof

- [ ] Exact public URL opened in a real browser.
- [ ] Desktop viewport rendered.
- [ ] Mobile viewport rendered.
- [ ] Expected app marker present.
- [ ] `Page not found` absent.
- [ ] No uncaught exception.
- [ ] No relevant console error.

## Feature-route proof

- [ ] Authenticated session/fixture established if required.
- [ ] Exact affected tab/page opened.
- [ ] Original failing payload reproduced.
- [ ] Nullable collection cases covered: omitted, null, empty, populated.
- [ ] Requested interaction completed.
- [ ] Original error text absent.
- [ ] Layout/theme visually checked above and below navigation where relevant.

## Evidence report template

```text
Routing smoke test:
- root: [URL] — [result]
- deep route: [URL] — [result]
- JS/CSS MIME: [result]

Feature verification:
- route: [exact URL]
- role/session: [fixture]
- payload cases: [cases]
- interaction: [action]
- desktop/mobile: [result]
- console/runtime errors: [result]

Production isolation:
- production hashes/files: unchanged
```

Never collapse routing smoke testing and feature verification into one claim.