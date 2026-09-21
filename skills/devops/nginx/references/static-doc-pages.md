# Static doc/note pages under existing project prefixes

Session: 2026-09-20, publishing Balikpapan Dev internal direction notes as a public styled HTML page with a client-side password gate at `/projects/balikpapan-dev/notes/direction-2026-09-19.html`.

## Serving a sub-path under an existing project

An SPA project like `/projects/balikpapan-dev/` already has:

```nginx
location /projects/balikpapan-dev/ {
    alias /var/www/html/projects/balikpapan-dev/;
    index index.html;
    try_files $uri $uri/ /projects/balikpapan-dev/index.html;
}
```

A standalone static HTML file at `/var/www/html/projects/balikpapan-dev/notes/<name>.html` is served **as-is** by this block (no nginx edit, no reload). Caveats:

- The SPA fallback only kicks in for non-existent URIs, so the real file wins.
- Watch for competing `location = /projects/<name>` catch-all `return 404` blocks on other slugs — check the whole server block first.
- Reuse existing assets (logo) via absolute path `/projects/<name>/assets/...` — they resolve through the same alias.

## Pitfall: write_file creates 0600 files → nginx 403

`write_file` (and similar tooling) creates files with `umask`-derived `0600` (`-rw-------`) even though the parent dir is `drwxrwxr-x`. nginx workers run as `www-data` and get **403 Forbidden**. Existing files in these dirs are `0644` (`-rw-rw-r--`), which works.

Fix after every new static file:

```bash
chmod 644 /var/www/html/projects/<name>/notes/<file>.html
```

Diagnostic tell: `curl` returns 403 but a sibling file in the same dir returns 200, and the dir perms look fine → check the **file** mode bits, not just the dir.

## Client-side password gate pattern

For informal/internal notes that must be public-URL accessible but not open to everyone:

- Lock screen: fixed overlay div, password input, inline error text.
- Compare SHA-256 hex of the input against a hardcoded hash constant — never embed the plaintext password.
- Generate hash once: `python3 -c "import hashlib;print(hashlib.sha256('the password'.encode()).hexdigest())"`.
- `crypto.subtle.digest` requires a **secure context** (https or localhost) — pages are served over https on this host, so fine.
- Store re-auth flag in `sessionStorage` (per-tab, dies on close) — lighter touch than localStorage.
- `<meta name="robots" content="noindex">` so gated content stays out of search engines.
- Understand and state the ceiling: client-side gating is obfuscation, not security (page source contains the content). Fine for "don't stumble onto it" internal notes; never for real secrets.

## Mermaid in static pages

- Mermaid v11 ESM from CDN: `import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs'` in a `<script type="module">`.
- Initialize with `startOnLoad: false`, then render after unlock: `mermaid.run({ querySelector: '.mermaid' })` — avoids rendering while the content div is `display:none` (mermaid measures layout).
- Diagram source goes in `<div class="mermaid">`; browsers strip per-line leading whitespace from `.textContent`, so indented multi-line flowcharts inside HTML work fine.
- Dark theme via `theme: 'dark'` + `themeVariables` (`primaryColor`, `primaryBorderColor`, `lineColor`) to match the page palette.

## Verification when browser tools are unavailable

If the browser stack can't run (timeout on navigate), verify a published gated page with node instead:

```js
// 1. hash check: sha256 of expected password === HASH constant in page; wrong pw !== HASH
// 2. count and parse <div class="mermaid"> blocks: strip tags, trim lines, first line must be `flowchart TD|LR`
// 3. assert required content strings (corrections, keywords) present in the HTML
```

Plus `curl` the public URL for HTTP 200 and check the response is the expected HTML, not an SPA fallback.

## Keeping source-of-truth notes in sync

When publishing a rendered HTML version of a markdown note (e.g. `~/notes/<topic>.md`), apply any user corrections to **both** the HTML page and the source markdown — otherwise the md goes stale and a future re-publish loses the corrections.
