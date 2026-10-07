# Markdown-first live editor integration

Use this pattern when replacing a split Markdown textarea/preview with a rich editor while preserving Markdown as the backend contract.

## Minimal implementation sequence

1. Confirm the current persistence contract and keep it unchanged (for example, `content_markdown` remains canonical rather than storing generated HTML).
2. Add a source-level acceptance test first that requires the editor package imports, Markdown update listener, final Markdown extraction, and removal of the old textarea/preview.
3. Verify the test fails for the missing feature before editing production code.
4. Instantiate the editor only in the framework's client mount lifecycle. Bind it to a real DOM root, initialize from existing Markdown, and destroy it on unmount.
5. Update local form state through the editor's Markdown-change listener. Immediately before submit, extract Markdown directly from the editor as a final synchronization guard.
6. Preserve existing title validation, save APIs, navigation, error handling, and accessibility labels. Replace only the editing surface.
7. Scope editor CSS beneath a component wrapper so generic classes from the editor package do not leak into the application. Include mobile height/padding rules.
8. Record the feature in the project changelog.

## Verification

Run the focused test, full tests, framework/type checks, and production build. If the application is served from copied static output, deploy the new build rather than stopping after source/build/push. Verify the exact public route and confirm a newly generated asset contains a feature marker or the deployed HTML references the new asset hashes. Then commit only intended paths, push, and prove local HEAD equals the remote branch SHA.

## Pitfalls

- Do not make rendered HTML the source of truth when the API stores Markdown.
- Do not rely solely on asynchronous change callbacks; extract current Markdown again on save.
- Do not initialize DOM-dependent editors during SSR or module evaluation.
- Do not leave the old preview pane or toolbar in place unless the selected editor requires it.
- Large lockfile growth is expected for editor ecosystems, but inspect dependency/license information and avoid adding optional plugins before they are needed.
