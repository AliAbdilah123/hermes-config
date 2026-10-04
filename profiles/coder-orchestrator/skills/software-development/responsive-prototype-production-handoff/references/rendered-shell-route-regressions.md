# Rendered shell and route regression recipe

Use for authenticated SPA shell migrations involving detail/list destinations, history restoration, early-return routes, and modal mobile navigation.

## Test bootstrap

- Put the exact route in `history` before rendering.
- Mock every startup endpoint required to settle the application, using exact response shapes. Nullable endpoints must return `null`, not a truthy placeholder such as `[]`; otherwise unrelated dialogs can open and hide the route under test.
- Wait for a route-specific landmark before interacting. Shell presence alone does not mean route loading finished.

## Detail to list navigation

Render each detail URL, click the real shell destination, and assert both the list landmark and canonical list URL. Do not let “active top-level section” act as “already at exact destination”: project detail and Projects list share a section but are distinct routes.

## Transactional restoration

For `popstate`, parse and load the complete destination first. Hold loaded detail/items/settings in locals, then commit related state together. On failure, retain the prior rendered view and expose accessible error feedback; never set the destination view before its data succeeds.

Test failure by:

1. Rendering a known stable route.
2. Replacing history with a destination whose API fails.
3. Dispatching `PopStateEvent`.
4. Asserting an alert plus the unchanged prior landmark.

## Shared-shell early routes

Routes previously returned before the shell must render as shell children or through a real shell variant. Assert primary desktop navigation, mobile opener, account context, and the route surface together. Wrapper classes are not shell integration.

## Dialog drawer close

If the dialog primitive supplies an unconditional close control, remove the custom close rather than stacking both. Query its actual accessible name, assert exactly one close button, click it, and assert dialog closure. Also retain Escape/focus-return coverage.

## CSS collision control

Replace broad `header`/`nav` selectors with explicit application classes before introducing a new shell. Do not run blind textual replacements such as `header` → `.app-header`: they corrupt compound selectors (`.conversation-page-header`, `.dialog-shell-header`). Patch complete selectors and immediately search for malformed fragments. Consolidate superseded declarations in place instead of appending a final override layer.

## Evidence

Capture RED from focused rendered tests, then GREEN from the focused behavior. Final evidence should include the complete project test command, production build, and `git diff --check`. If canonical-command detection misses project scripts, run them through a secure `mktemp /tmp/hermes-verify-XXXXXXXX.sh` wrapper, remove it via `trap`, and label the result ad-hoc verification.
