# Frontend envelope + form contract regressions

Use when a React/Vite page throws `.filter is not a function` / `.map is not a function` after adding or changing API-backed form fields, or when create/edit forms appear to save but later hydrate blanks.

## Durable pattern

1. Trace the failing value to the API client helper, not only the page line using `.filter()`.
2. Probe the real endpoint shape. In Komuna-style Go handlers, list routes often return `{ data: [...] }`, while convenience helpers may be typed as `T[]` by mistake.
3. Fix at the shared API helper or consumption boundary:
   - If a helper is named `listX(): Promise<X[]>`, unwrap `{ data }` inside the helper.
   - If a page consumes both raw arrays and envelopes, add a tiny normalizer (`Array.isArray(value) ? value : value.data ?? []`).
4. For create/edit form fields, verify the full round trip, not just the outgoing payload:
   - frontend payload key
   - backend decode key
   - database write
   - detail/list query select/scan
   - DTO response key
   - edit-form hydration key
5. Watch for case-style drift: frontend payloads may use `camelCase`, database/DTO fields may use `snake_case`. If persisted JSON stores camelCase, edit hydration must either normalize on read or support both shapes.
6. Backend guardrails should mirror UI guardrails for destructive relation edits. Example: if products require at least one manager, both product edit and member-role revoke endpoints must reject removing the last manager.

## Minimal verification

- Unit/API test for required relation persistence.
- Typecheck/build for the page.
- If deployed, grep/fetch the served hashed bundle for unique literals from the fix and hit `/health` after restart.
