# Provider-specific composer terminology

When providers use different public vocabulary for the same internal publish primitive, keep the existing API/storage type stable and adapt only the rendered label.

## Pattern

- Derive the visible label from the selected destinations at render time.
- Do not add a duplicate post type or alter the publish payload for a copy-only distinction.
- Example: a Threads-only video can remain internal type `REEL` while displaying **Video**. Instagram-only and mixed Instagram/Threads destinations retain **Reel**.
- Add focused tests for the provider-only label plus the ordinary and mixed-platform fallbacks.

## SocialZen frontend deployment gate

The frontend build runs under `apps/frontend`, so its artifact is `apps/frontend/dist/`, not repository-root `dist/`. Copy that artifact to the configured live web root. Deployment is not READY until the public route is exercised. If authenticated public E2E cannot be completed, report deployment and verification separately; do not imply full verification.
