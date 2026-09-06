---
name: dashboard-api-contract-debugging
description: Diagnose and verify React dashboard crashes caused by API shape drift, nullable nested collections, and route/state-specific behavior.
version: 1.0.0
metadata:
  hermes:
    tags: [react, dashboard, api-contract, debugging, verification]
---

# Dashboard API Contract Debugging

Use when a React dashboard route throws collection errors such as `Cannot read properties of null (reading 'filter')`, `.map is not a function`, or null `.length`, particularly when a previous normalization fix did not resolve the exact tab.

## Core rule

A working landing page, HTTP 200, valid assets, or a normalized top-level response does not prove the reported dashboard feature works. Reproduce and verify the exact route, role, state, and runtime payload.

## Workflow

1. Capture the exact route, role, error text, and state that triggers the crash.
2. Probe or fixture the real endpoint response shape. Treat TypeScript DTOs as hypotheses.
3. Normalize top-level envelopes (`data`, `items`, named collections) to arrays at the API consumption boundary.
4. Continue tracing downstream. Search the feature directory for `.filter(`, `.map(`, `.flatMap(`, and collection `.length` access. Test nested fields independently; common failures include `member.roles`, `weekly_slots`, claims, and child arrays being `null`.
5. Write a route-level regression test first. Use realistic payloads and set one candidate nested collection to `null`. Run it and require the exact reported TypeError before changing production code.
6. Fix at the mapper or DTO boundary with the smallest normalization, usually `(value ?? [])`. Do not scatter optional chaining throughout render code.
7. Run the focused test, neighboring route tests, typecheck/build, and changed-file lint. Keep unrelated baseline failures separate.
8. Verify the exact feature route with a real authenticated browser session when available. If authentication is unavailable, report the route-level regression as evidence and explicitly leave live authenticated verification pending; do not substitute homepage rendering.

## Theme ownership during dashboard fixes

When asked to move a visual theme above tab containers, put theme tokens and page background on the shared dashboard shell/layout. Tab/page components should inherit tokens and use transparent backgrounds. Add a structural test asserting the shell owns the tokens/background and the tab component no longer redeclares them.

## Verification standard

- Exact reported error reproduced before the fix.
- Each nullable nested collection tested independently.
- Expected route content renders and alert/error content is absent.
- Shared-shell visual ownership is mechanically asserted when changed.
- Preview infrastructure verification and feature-route verification are reported as separate boundaries.

See `references/nested-null-collections-and-feature-route-verification.md` for a compact reproduction and preview checklist.

## Startup auth loading loops

When an SPA stays forever on its workspace/bootstrap loader and never exposes Login/Register, inspect persisted auth before treating it as a dashboard API outage. A stale non-empty token can initialize the client as authenticated while the authoritative `/me` request fails and leaves workspace/onboarding state `null`. Clear the persisted credential and all auth-derived state at the saved-session restoration boundary so the existing unauthenticated route renders. Do not clear a valid session for failures from secondary dashboard fan-out endpoints.

Verify by seeding an invalid token before public browser navigation, then assert login is visible, loading copy is absent, persisted auth is cleared, and no uncaught page error occurs. See `references/stale-saved-auth-loading-loop.md`.

## Plain-text error responses parsed as JSON

When a CRUD form reports `Unexpected token '<letter>'`, inspect the shared fetch wrapper before changing the form. Parsing every body as JSON before checking HTTP status can mask a useful plain-text error returned by Go `http.Error`, a proxy, or a legacy endpoint. Preserve the text on failed responses, keep malformed successful JSON as a protocol error, then investigate any underlying server rejection separately.

See `references/plain-text-http-errors-masked-by-json-parsing.md` for the diagnosis, minimal fix, and authenticated persistence verification recipe.

## Pitfalls

- Fixing `weekly_slots: null` while overlooking `member.roles: null` in a downstream manager mapper.
- Assuming one top-level `items()` helper protects nested arrays.
- Claiming a Sessions or Members tab is fixed because the public preview homepage renders.
- Moving only the theme toggle control when the request concerns theme background/token ownership.
- Repeating a preview URL after checking only HTTP status, asset hashes, or a generic deep route.
