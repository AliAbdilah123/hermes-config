# Model-driven A2UI chat delivery

Use for chat applications that call a local OpenAI-compatible router and render structured model output through a real A2UI processor/renderer.

## Minimal safe architecture

- Keep router credentials server-side. The browser calls a same-origin application endpoint; the server calls the local router with the exact requested model ID.
- Probe the router contract before implementation: model listing, authentication requirement, chat endpoint, structured-output behavior, and the model ID reported by the app contract.
- Ask the model for a bounded JSON content model, not arbitrary A2UI component definitions. Normalize string lengths and item counts, then map that normalized data into a bundled, trusted A2UI component tree. This preserves genuine protocol rendering while constraining phishing, XSS, and layout-complexity risks.
- Validate request history count, roles, per-message lengths, total body size, and upstream error shapes.
- Leave a focused protocol-flow test asserting surface creation, component update, data update, limits, and action-to-chat conversion.

## React renderer lifecycle pitfall

Some A2UI surface models are callable/proxy-like objects. Passing React's state setter directly as a subscription callback can make React interpret the model as a functional state updater and invoke it, producing a minified `TypeError: ... is not a function` only after the first generated surface.

Do not write `processor.onSurfaceCreated(setSurface)`. Wrap the value (`surface => setSurface(() => surface)`). If React still treats the model specially, store it in `useRef`, increment a numeric render version in state, and render `surfaceRef.current`.

Verify the first real model response in a production browser build; an empty shell does not exercise this failure.

## Shadow-DOM and custom-element contrast

A2UI renderer-owned text may ignore normal descendant CSS. Set documented A2UI color variables on the outer generated-surface container so they inherit through custom-element boundaries, and set variables/color on relevant custom-element hosts when required. Verify screenshots: DOM text presence does not prove readable contrast.

## Root-domain nginx routing

If a generic wildcard project server rewrites `/` to an internal `/projects/<slug>/` path, adding a location that matches only the rewritten URI may not reliably supersede the existing bridge. Prefer a dedicated exact `server_name` block for a backend-dependent app, proxying the entire root domain to its application service. Test with `curl --resolve` or an explicit Host header before public HTTPS.

Public CDN caches can temporarily serve the old static shell after switching the origin. Verify with a unique query parameter and `Cache-Control: no-cache`, then ensure hashed assets and the API endpoint come from the new service. Do not mistake stale HTML at one cache key for an origin routing failure.

## Public acceptance

1. Run tests and production build.
2. Start the built app as its deployed service and probe health, root HTML, a valid live model call, and an invalid-request rejection.
3. In a real browser at desktop and mobile widths, send a message and wait for the generated surface.
4. Assert user and assistant turns, renderer-owned surface content, no horizontal overflow, no runtime/console errors, and no error state.
5. Capture screenshots and inspect text contrast, sticky-header layering, and fixed-composer overlap. A fixed composer requires enough scroll padding for the final generated component to clear it.
6. Rebuild/restart after every visual correction and repeat the public browser flow against the new hashed assets.
