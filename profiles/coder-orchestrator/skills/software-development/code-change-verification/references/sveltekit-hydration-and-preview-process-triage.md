# SvelteKit hydration and preview-process triage

Use when SSR HTML looks correct but client interactions fail, client navigation changes the URL without replacing content, or browser E2E appears to hit stale behavior.

## Separate application faults from harness/process faults

1. Capture `pageerror`, console errors, failed requests, resulting URL, and a stable DOM marker after the interaction.
2. Test a trivial hydrated interaction (for example, a password visibility toggle) and the failing route both through client navigation and direct loading.
3. If the URL changes but old content remains, directly load the destination route. A direct-load runtime exception isolates route hydration from link behavior.
4. Inspect the transformed Svelte module only to confirm expected event registration exists; source compilation does not prove runtime hydration.

## Svelte 5 bindable fallback mismatch

A child component may declare a bindable DOM ref with a fallback:

```svelte
let { ref = $bindable(null) } = $props();
```

The parent must initialize the bound value compatibly:

```svelte
let area = $state<HTMLTextAreaElement | null>(null);
<Textarea bind:ref={area} />
```

Initializing it as `undefined` (for example, `$state<HTMLTextAreaElement>()`) can throw `props_invalid_value` during hydration because a bound prop with a child fallback cannot receive `undefined`.

Verification sequence:

- Add a focused regression asserting the parent initializes the bound ref to the child fallback value.
- Observe RED.
- Apply the one-line initialization fix.
- Run the focused/full tests, typecheck, and build.
- Direct-load the affected route and require no `pageerror` before replaying the full flow.

## Exact preview listener discipline

Vite launched through `npm run dev` or `npm run preview` may have a child process that outlives the tracked shell parent. A new launch without strict port handling can silently move to another port, while E2E continues testing the stale listener.

Before browser verification:

1. Inspect the tracked process output and the actual listening socket.
2. Stop the exact project-local Vite child/listener; do not assume killing the shell parent freed the port.
3. Build serially after any cleanup of `.svelte-kit`; preview requires fresh server output.
4. Start preview on a dedicated port with `--strictPort`.
5. Wait for the explicit `Local:` readiness line and confirm the process remains running.
6. Point the harness at that exact port. Never accept Vite's automatic fallback port during deterministic E2E.

Classify failures precisely: connection refusal is readiness/setup; a locator mismatch after correct navigation is harness behavior; a direct-route `pageerror` is an application defect.