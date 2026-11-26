# Canonical frontend artifact fidelity

Use when rebuilding an API-backed frontend from a static HTML/CSS prototype that is the visual contract.

## Workflow

1. Confirm the requested repository is clean and create the requested branch from the exact current base before editing.
2. Read the **entire** artifact, including responsive and reduced-motion rules. Extract its CSS without reformatting when exact fidelity is required; preserve selectors and composition instead of approximating the design system.
3. Inventory the existing frontend types, API calls, tests, and backend routes before replacing UI code. Build a small mapping from each prototype surface/action to its real endpoint and role restriction.
4. Recreate every specified surface with persisted API data. Keep the prototype's layout slots when data exists, but omit metrics, records, buttons, or interactions that lack a backend contract rather than inventing values or no-op functionality.
5. Preserve shared navigation and role-aware controls. Ensure lesson/package actions use actual IDs rather than a hard-coded first record when the contract permits it.
6. Retain trust-boundary validation, accessible names/status regions, keyboard focus, 44px mobile targets, overflow containment, and `prefers-reduced-motion` behavior.
7. Update focused tests for navigation plus mutations on both learner and admin paths: login, lesson completion, reward request/create/decision, and invite creation as applicable.
8. Run the exact requested test and build commands separately. Treat warnings or unhandled runtime errors as verification failures even if the test assertions pass; fix or explicitly mock unsupported browser APIs in the test environment.
9. Report only source files intentionally changed. Generated build output should not be presented as source work unless tracked and requested.

## Pitfalls

- A passing assertion count is not a clean test run when the runner reports an unhandled exception or browser-API warning.
- Do not claim exact visual matching from CSS reuse alone. Verify rendered routes at representative desktop and mobile widths when browser tooling is available.
- Avoid replacing a real API action with a prototype toast. A visual prototype describes composition, not the application contract.
- Do not preserve fake prototype statistics merely to fill cards; derive them from persisted values or omit/relabel the card.
- Static prototypes often hard-code names, dates, counts, and package copy. Bind all available equivalents and avoid implying unavailable backend state.
