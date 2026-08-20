---
name: spa-auth-session-recovery
description: Diagnose and fix SPAs that retain client auth state after the server session cookie is missing, expired, or rejected, especially when several protected modules show raw 401 JSON.
---

# SPA Auth Session Recovery

Use when an SPA still appears signed in while multiple unrelated protected pages fail with `401`, raw JSON, or session errors.

## Workflow

1. **Classify the server response.** Inspect `/auth/me`, protected API requests, and access/service logs. Distinguish missing cookie (`unauthorized`) from an unknown persisted session (`session_not_found`) and signature/secret rejection (`bad_session`).
2. **Trace both auth stores.** Identify the HttpOnly session cookie and any durable client marker such as CSRF, account, or local-storage state. A missing cookie plus retained client state is a split-brain UI.
3. **Check deployment scope.** Verify whether recent changes touched authentication. A restart does not explain a missing browser cookie when sessions and signing secrets persist.
4. **Fix once at the shared API boundary.** On protected-route 401, clear stale client auth and notify the root application to render Login. Exclude public authentication endpoints to avoid loops.
5. **Keep errors structured.** Preserve status/code/data for code paths, but render clean user-facing copy instead of raw response JSON.
6. **Keep unexpected failures observable.** Suppress only the expected recovery 401 during root bootstrap; continue reporting network, 5xx, and unrelated failures.
7. **Verify both halves publicly.** Prove stale-state recovery and a subsequent valid login at the exact production origin.

## Guardrails

- Do not patch Prospect, Offers, CRM, or other page components separately when they share the same API client.
- Do not alter backend cookie/session behavior unless evidence shows a valid cookie was sent and rejected.
- Do not infer secret rotation from a generic 401; response codes and request-cookie evidence must support it.
- An expected browser network 401 can appear as a console resource warning. Treat uncaught `pageerror` and application `console.error` separately from transport diagnostics.

## Verification

Require focused tests for protected routes, public auth exclusions, clean error messages, notification/clear behavior, and preservation of unexpected error reporting. Public E2E should start with stale client state and no cookie, assert Login plus cleared state and no raw JSON, then perform a real login and assert authenticated chrome.

See `references/stale-client-auth-missing-session.md` for the compact diagnosis and E2E matrix.
