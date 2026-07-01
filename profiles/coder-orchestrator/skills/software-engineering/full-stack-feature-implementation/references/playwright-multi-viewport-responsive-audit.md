# Playwright Multi-Viewport Responsive Audit

Use when you need to programmatically detect responsive issues (horizontal overflow, text clipping, off-screen elements) across multiple viewport sizes — more thorough than visual screenshots alone.

## When this applies

- User reports "pages are not responsive" without specifying which pages or breakpoints.
- You need to audit all auth-gated pages at multiple viewport widths (desktop, tablet, mobile-L/M/S).
- The Hermes browser tool times out on the SPA (see also `headless-chromium-mobile-screenshot-qa.md` for the simpler screenshot-only approach).
- You want automated detection, not just visual inspection.

## Setup

```bash
# Install Playwright + Chromium (one-time, ~110MB)
npx --yes playwright@latest install chromium
npm install playwright   # in a temp dir like /tmp
```

System Chromium snap at `/snap/bin/chromium` also works as `executablePath`.

## Script template

Write a Node script (`/tmp/check-responsive.js`) that:

1. **Logs in via API** to get an auth token.
2. **Loops over viewport sizes**: `[1440,900], [768,1024], [414,896], [375,667], [320,568]`.
3. **For each viewport**, creates a new context, injects the token into `localStorage` via `page.addInitScript`, navigates to the SPA, then clicks through pages (avatar menu → Memberships/Dashboard/Profile, tab buttons, product cards).
4. **At each page**, runs `page.evaluate()` to check:
   - `document.documentElement.scrollWidth > clientWidth` → horizontal overflow
   - `el.scrollWidth > el.clientWidth` with `overflow:hidden` → text clipping
   - `el.getBoundingClientRect().right > viewportWidth` → off-screen elements
5. **Reports** all issues with element tags, classes, and dimensions.

Key patterns:

```js
const browser = await chromium.launch({
  executablePath: '/snap/bin/chromium',
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
});

// Inject auth token before page loads
await page.addInitScript((t) => {
  window.localStorage.setItem('mt_auth_token', t);
}, token);

// Navigate via UI (Radix dropdown menus need click + waitForTimeout)
await page.click('.avatar-button');
await page.waitForTimeout(300);
const items = await page.$$('.avatar-menu button');
for (const item of items) {
  const text = await item.textContent();
  if (text?.includes('Memberships')) { await item.click(); break; }
}

// Check horizontal overflow
const dims = await page.evaluate(() => ({
  scrollW: document.documentElement.scrollWidth,
  clientW: document.documentElement.clientWidth,
}));

// Find culprit elements overflowing viewport
const culprits = await page.evaluate((vw) => {
  const r = [];
  document.querySelectorAll('*').forEach((el) => {
    const rect = el.getBoundingClientRect();
    if (rect.right > vw + 2) {
      const s = window.getComputedStyle(el);
      if (s.display !== 'none' && s.visibility !== 'hidden')
        r.push(`<${el.tagName.toLowerCase()}> cls="${el.className?.toString?.()?.slice(0,60)}" R=${Math.round(rect.right)} W=${Math.round(rect.width)}`);
    }
  });
  return r.slice(0, 5);
}, viewportWidth);

// Check text clipping
const textIssues = await page.evaluate(() => {
  const r = [];
  document.querySelectorAll('h1,h2,h3,h4,p,button,span,strong,th,td').forEach((el) => {
    if (el.offsetWidth === 0) return;
    const s = window.getComputedStyle(el);
    if (s.display === 'none' || s.visibility === 'hidden') return;
    if (el.scrollWidth > el.clientWidth + 2 && s.overflowX === 'hidden') {
      r.push(`<${el.tagName.toLowerCase()}> "${el.textContent?.trim().slice(0,50)}" sW=${el.scrollWidth} cW=${el.clientWidth}`);
    }
  });
  return r.slice(0, 5);
});
```

Set `page.setDefaultTimeout(5000)` to avoid 30s hangs on missing elements. Wrap all navigation in try/catch.

## Step 0: Check viewport meta tag FIRST

Before running any Playwright audit, verify the HTML has a viewport meta tag. This is the #1 cause of "not responsive on mobile" reports — all CSS media queries are correct but never trigger because mobile browsers default to a ~980px virtual viewport.

```bash
# Quick check
curl -s <url> | grep -i 'viewport'
```

Or in Playwright:
```js
const hasViewport = await page.evaluate(() =>
  !!document.querySelector('meta[name="viewport"]')
);
if (!hasViewport) {
  issues.push('MISSING viewport meta tag — mobile browsers will render desktop layout');
}
```

Also verify the HTML has proper structure (`<!DOCTYPE html>`, `<html>`, `<head>`, `<body>`). A bare `<div id="root">` + `<script>` with no `<head>` means the meta tag can't exist. This is common in minimal Vite SPAs where the `index.html` was hand-written as a one-liner.

## Common responsive issues this detects

0. **Missing viewport meta tag** (check FIRST) — without `<meta name="viewport" content="width=device-width, initial-scale=1">`, mobile browsers use a ~980px virtual viewport and zoom out. All `@media` queries are dead code. Fix: add the meta tag to `index.html` `<head>`.
1. **Brand text clipping** — `white-space:nowrap` + `max-width:Xvw` on brand/heading text that's too narrow for the text content. Fix: hide text at small breakpoints, show only logo mark.
2. **Slide-in drawer off-screen overflow** — drawer panel uses `transform:translateX(110%)` to hide, but parent only has `opacity:0`. The panel is still in layout flow and triggers overflow. Fix: add `visibility:hidden` + `overflow:hidden` to parent when closed; move slide transform to `:not(.open)` selector.
3. **Fixed-width grid columns** — `grid-template-columns` with `minmax(18rem,...)` on all breakpoints. Fix: collapse to single column at mobile breakpoints.
4. **`shrink-0` + `whitespace-nowrap` on buttons** — shadcn Button base classes prevent shrinking in flex containers. Fix: override with `width:100%` in mobile media queries for button containers.

## Pitfalls

- **Radix dropdown menus** need `waitForTimeout(300)` after trigger click before querying menu items — they animate in.
- **Context closing unexpectedly** — if `page.goto()` fails and throws, the context may close. Wrap in try/catch and create a fresh context per viewport.
- **Script may hang after all checks** — the browser process can linger. Set a script-level timeout or call `browser.close()` in a finally block.
- **Vite dev server** needs `VITE_API_PROXY` env var to proxy API calls to the backend. The production build uses `import.meta.env.BASE_URL` for API paths, so serve dist under the correct base path.
- **A Playwright test at mobile viewport may show no overflow even without a viewport meta tag** — because Playwright sets the viewport directly via `viewport: { width: 375 }`, bypassing the mobile browser's virtual viewport behavior. To catch the missing-meta-tag issue, explicitly check for the meta tag in the DOM (Step 0 above), or test with `isMobile: true, hasTouch: true` context options which are closer to real mobile behavior. The definitive test is checking the meta tag exists.
