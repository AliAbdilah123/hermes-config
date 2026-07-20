# Go-Embedded SPA and Timeline-Link Verification

## Compare hashes at each boundary

```bash
# Embed directory
grep -oE 'assets/index-[A-Za-z0-9_-]+\.(js|css)' internal/board/web/index.html

# Compiled executable
strings bin/app | grep -oE 'index-[A-Za-z0-9_-]+\.(js|css)' | sort -u

# Running service
curl -fsS http://127.0.0.1:PORT/ \
  | grep -oE 'assets/index-[A-Za-z0-9_-]+\.(js|css)'

# Public route
curl -fsS 'https://HOST/PREFIX/?v=DEPLOY_ID' \
  | grep -oE 'assets/index-[A-Za-z0-9_-]+\.(js|css)'
```

Mismatch interpretation:

- New source/embed, old executable/public: rebuild backend binary and restart.
- New executable/local, old public: inspect proxy/CDN caching or wrong upstream.
- New JS, old CSS: frontend publication copied assets incompletely.

Build from the package that owns `main`, e.g.:

```bash
go build -o bin/app ./cmd/app
systemctl restart app.service
```

## Exact-record link diagnosis

1. Query the reported job and its timeline events from runtime storage.
2. Preserve the exact URL text, including line breaks and punctuation.
3. Render that content through the active timeline component.
4. Assert the anchor exists and has the canonical `href`.
5. Inspect CSS for the timeline bubble anchor.

A useful visible style is:

```css
.bubble a {
  color: #bfdbfe;
  text-decoration: underline;
  text-underline-offset: .15em;
}
.bubble a:hover { color: #dbeafe; }
.bubble a:focus-visible { outline: 3px solid #93c5fd; outline-offset: 2px; }
```

Use project tokens where available. Keep selectors scoped so unrelated navigation and buttons are unaffected.

## Done means

- Semantic test proves URL-to-anchor conversion.
- CSS regression check proves the scoped visible treatment exists.
- Frontend test/build and backend tests pass.
- Compiled executable contains the new asset hashes.
- Local and public HTML serve those hashes.
- Public CSS/JS contains a unique fix marker.
- The exact reported timeline entry is visibly link-colored and underlined on the reported viewport.
