# Subscription Xendit PRD Mobile Readability Correction

## What happened

The user said the public PRD page `https://komuna.ahsanworks.com/prd/subscription-xendit-plan.html` was hard to read on mobile. The first response misunderstood the request and added responsive-design requirements to the implementation plan content. The user corrected this: they wanted the **review page itself** made responsive, and a reusable Hermes skill so future Komuna plan pages are responsive and theme-aligned.

## Durable lesson

When a Komuna user says a `/prd/*.html` or review link is hard to read, treat it as a presentation bug in the published HTML artifact first. Do not add a plan requirement about future implementation unless explicitly requested.

## Correct workflow

1. Revert any accidental content-only additions that were meant for the product plan rather than the review artifact.
2. Patch the HTML artifact CSS/layout directly.
3. Preserve the Komuna dark warm theme.
4. Verify the public link with a cache-busting query string.
5. If possible, produce a 390px-wide browser screenshot and inspect for readability/horizontal overflow.

## CSS fixes that worked

- Add viewport meta if absent.
- Use responsive container width: `width:min(100% - 20px, 1120px)`.
- Collapse desktop sidebars under ~880px.
- Convert tables into block/card-like rows under ~560px.
- Set `main, .card { min-width:0; }` for grid overflow safety.
- Set `pre { max-width:100%; overflow-x:auto; -webkit-overflow-scrolling:touch; }`.
- Add `html, body { overflow-x:hidden; }` if screenshots reveal a tiny horizontal strip.

## Verification evidence pattern

Use these checks in future sessions:

```bash
curl -sI 'https://komuna.ahsanworks.com/prd/<slug>.html?v=mobile-check'
curl -sS 'https://komuna.ahsanworks.com/prd/<slug>.html?v=mobile-check' \
  | grep -E 'viewport|@media|max-width|overflow-x'
chromium-browser --headless --no-sandbox --disable-gpu \
  --window-size=390,900 \
  --screenshot=/tmp/<slug>-mobile.png \
  'https://komuna.ahsanworks.com/prd/<slug>.html?v=mobile-check'
```

Then inspect the screenshot for readable text, theme match, clipped content, and horizontal overflow.
