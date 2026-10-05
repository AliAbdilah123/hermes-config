# Capability-first feature delivery

Before adding backend code for a requested full-stack feature, inspect the existing API, schema, tests, and UI separately. The capability may already exist server-side and only need the thinnest missing client path.

When the backend already supports it:

1. Reuse the established endpoint and its validation.
2. Reuse the existing post-success token/session and data-loading flow.
3. Add only the missing UI state and accessible fields.
4. Add one focused UI test proving the exact request payload and transition into the authenticated experience.
5. Run the repository's canonical full check after reviewing the diff.

Avoid duplicating registration, authentication, validation, or workspace creation logic in the client or a second backend route.