# Loading feedback for API-triggering controls

Use this checklist when adding pending-state feedback across an existing frontend.

## Audit by behavior, not element name

Search every route/component for controls whose handlers call the API directly or through a helper. Include:

- form submit buttons and authentication flows
- icon-only actions
- menu actions
- table/list navigation that fetches detail data
- dialog confirmations
- tabs or custom controls that fetch on selection
- handlers that return helper promises such as `action("retry")`

Do not blindly replace every button: purely local toggles, dialog close controls, and navigation without async work do not need a pending state.

## Minimal reusable behavior

Prefer the existing shared button primitive. If none can own async behavior safely, add one focused wrapper that:

1. accepts an event handler returning `void | Promise<void>`
2. sets pending before awaiting the handler
3. disables while pending to suppress duplicate submissions
4. sets `aria-busy=true`
5. restores the original label and enabled state in `finally`
6. preserves an externally supplied `disabled` state
7. supports a concise custom pending label for icon-only controls

For native form submission, the form may own the pending state instead; guard duplicate submits and reset in `finally`.

## Test-first checks

Before implementation, render the wished-for shared control with a manually resolvable promise and verify the test fails because pending behavior is absent. Then assert:

- the control disables immediately
- `aria-busy` is announced
- pending text appears
- a second click does not invoke the action again
- resolution restores the original state
- a handled rejection also restores the original state

Run the focused frontend test, the complete frontend suite, the production frontend build, and the backend suite if frontend assets are embedded.

## Embedded-SPA deployment

A frontend build may only copy hashed assets into an embed directory. If the backend embeds those files, rebuild the executable at the service manager's actual `ExecStart`, restart it, wait with bounded retries, and fetch live HTML to confirm the new asset hash. A generic HTTP 200 alone does not prove the new bundle is serving.
