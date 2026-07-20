---
name: embedded-spa-deployment-debugging
description: Debug and verify SPAs whose generated assets are embedded into compiled backend binaries, including stale bundles and visually invisible rendered behavior.
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [deployment, debugging, vite, react, go-embed, frontend]
---

# Embedded SPA Deployment Debugging

Use this when frontend source/tests say a fix exists but a compiled backend application still serves old or apparently unchanged UI.

## Artifact chain

Treat deployment as four distinct artifacts:

1. Frontend source.
2. Generated frontend assets (`dist/` or the backend embed directory).
3. Compiled backend executable.
4. Assets served locally and publicly by the running process.

Never infer deployment from source or build success alone. Compare hashed JS/CSS names at every boundary. For Go `embed.FS`, copying new files into the embed directory does not modify an existing executable; rebuild the executable from the actual main package and restart it.

## Workflow

1. Reproduce the exact reported record and inspect its stored content.
2. Trace the active render component; rule out changes made to unused/legacy components.
3. Run semantic component tests and the production frontend build.
4. Inspect generated/embed HTML asset hashes.
5. Inspect asset names embedded in the executable.
6. Rebuild from the real entrypoint (commonly `./cmd/<app>`, not repository root).
7. Restart and verify process health.
8. Compare local and public HTML asset hashes with a cache-busting query.
9. Fetch public JS/CSS and check a unique marker from the fix.
10. Visually verify the exact reported screen and viewport.

## Semantic vs visual bugs

A DOM element can be functionally correct yet appear broken. For links:

- Confirm an `<a>` is emitted with the correct `href`.
- For external links, verify `target="_blank"` and `rel="noopener noreferrer"`.
- Confirm unsafe schemes remain plain text.
- Inspect scoped CSS: an anchor inheriting white text with no underline can look exactly like plain text.
- Provide explicit link color, underline, hover state, and `:focus-visible` outline.
- Add one semantic rendering test and one lightweight scoped-CSS regression assertion.

An HTTP 200 or a new JavaScript hash is not enough for a visual defect. Verify the CSS artifact and rendered appearance too.

See `references/go-embedded-link-visibility.md` for a concise command recipe and the link-rendering variant.

See `references/go-embedded-spa-stale-runtime.md` for the stale-binary evidence pattern, correct frontend→Go build→restart sequence, and hash-based local/public verification.
