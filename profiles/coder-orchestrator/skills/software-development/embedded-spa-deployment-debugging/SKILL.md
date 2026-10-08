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

For independently served static SPAs, separate the frontend artifact from the API service: restarting a healthy backend cannot repair missing frontend assets. Rebuild with the public mount path, atomically publish the complete clean output directory, and restart the API only if its runtime artifact or configuration also changed. After recovery, make the mount path part of the canonical deploy command/script or CI environment so a later root-base build cannot reintroduce the blank page.

## Standing post-implementation delivery gate

When the user has established that implementations must be deployed, treat every completed implementation—not only explicit deployment requests—as requiring the full runtime cycle before reporting completion:

1. Rebuild the production frontend artifact.
2. Publish the complete clean artifact to the active serving directory.
3. Restart the project service even for a frontend-only change when that is the user's established delivery workflow; this honors the requested lifecycle and removes stale-runtime ambiguity.
4. Poll local service/API health after restart.
5. Verify the canonical public URL and changed route/content. Use rendered browser E2E when available; if unavailable, report that limitation and provide public HTTP, asset MIME, and deployed bundle-marker evidence instead.
6. Only then report ready, including the public app link, commit, and push status.

Do not stop at source edits, tests, build success, or Git push. Those prove intermediate artifacts, not the running application.

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

See `references/safe-pull-rebuild-restart.md` for dirty-worktree handling, semantic stash comparison, rebuilding the executable named by systemd, readiness polling, and local/public verification.

See `references/static-spa-cache-safe-deployment.md` when fresh browsers render but some clients see a blank page after a hashed-asset deployment. It covers previous-generation asset probes, SPA-fallback MIME traps, immediate restoration, HTML cache policy, and compatibility-window cleanup.

See `references/nginx-static-spa-service-restart.md` for discovering the canonical Nginx hostname/mount, deploying a clean static build, restarting the separate API service when requested, and verifying public HTML, API health, MIME types, bundle markers, and rendered E2E.

See `references/sveltekit-static-subpath-build-base.md` when a SvelteKit static SPA returns HTML but stays blank under an Nginx subpath. It distinguishes a source defect from a deployment-build invocation that omitted `BASE_PATH`, and defines emitted-HTML, asset-MIME, and rendered-browser gates.
