# Verifying Repository Design-System Packages

Use this when adding an application-derived design-system package plus an interactive prototype to an existing catalog.

## Establish the repository contract first

Before authoring, inspect:

- the manifest schema;
- one complete neighboring package;
- manifest and package-quality checks;
- generators for component manifests, token reports, preview indexes, and system assets.

Copy a neighboring package's **structure**, not its derived output. Authored files commonly include `manifest.json`, `DESIGN.md`, `USAGE.md`, `tokens.css`, `components.html`, and an interactive preview. Generate repository-specific JSON/reports from those sources.

## Validation ladder

Run in this order:

1. Parse HTML/JSON and run `git diff --check`.
2. Run the manifest/schema checker.
3. Run package-quality checks.
4. Verify `tokens.css` ↔ component-fixture token synchronization.
5. Verify all declared derived artifacts are fresh.
6. Confirm catalog discovery through the runtime API or UI.
7. Serve the prototype and verify HTTP 200, console, interactions, desktop, and mobile layouts.
8. Run the broader focused repository guard.

Catalog discovery proves only registration, not visual or interactive correctness.

## Common pitfalls

- If `components.html` must embed canonical tokens, its first `:root` block may need to match `tokens.css` byte-for-byte after normalization.
- Component extraction commands may write an aggregate `{manifests:[...]}` wrapper while the checked-in per-package file expects the single inner manifest. Inspect a neighboring artifact before saving.
- Optional generated files declared in a manifest are normally freshness-checked. Regenerate them or omit the optional declaration/files when the schema permits; never keep copied stale output.
- Generator scripts can alter unrelated packages. Inspect `git status` immediately and remove unrelated generated changes before committing.
- Runtime package APIs may scan dynamically, so restart only when the actual lifecycle requires it.

## Delivery evidence

Record separately:

- package checks;
- prototype/browser/responsive checks;
- runtime/public-route checks;
- commit result;
- push result.

A local commit is not a successful push. If remote permissions reject delivery, state the exact boundary without claiming completion.
