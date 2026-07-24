# Single-card checkout composition

Use this pattern when a checkout must become one centered column and previously separate package/payment cards must read as one card.

## Minimal production pattern

1. Keep package and order components separate for SRP and existing tests/previews.
2. Add one outer page card with a bounded centered width (`max-width` plus `margin-inline: auto`) and responsive horizontal padding.
3. Give the order component an explicit embedded variant that removes its own outer border, radius, sticky positioning, and full padding while retaining a top divider and internal spacing. Preserve its standalone default for previews and direct tests.
4. Use native `<details open>` and `<summary>` for an initially expanded, keyboard-accessible collapsible package-entry list. Avoid React state unless custom animation or controlled persistence is explicitly required.
5. Add focused assertions that package and order content share the same outer card, the shell is centered/bounded, and the disclosure starts open and can close.

## Verification boundary

Run the full focused test file, changed-file lint, typecheck, and production build independently. If unrelated or pre-existing checks fail, also run the narrow new tests, but report both scopes exactly. Never mark verification complete or imply the feature is fully green while any requested gate is failing. A successful commit/push is not deployment; verify the live route only after the project’s real deployment step serves the committed artifact.

## Pitfalls

- Visually nesting two bordered cards instead of creating one outer card.
- Removing standalone card styling globally and breaking admin previews or isolated renders.
- Reimplementing disclosure state in React when native HTML already supplies accessible behavior.
- Calling a public homepage HTTP response proof that the new checkout bundle is deployed.
