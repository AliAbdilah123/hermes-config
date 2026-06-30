# SPA auth provider env and fallback debugging

Use this when a deployed SPA shows the wrong login UI after changing auth configuration (for example, hosted OAuth UI vs local email/password fallback).

## Durable lessons

1. **Identify the intended auth mode first.** Before wiring provider UI, confirm whether the project should use hosted/OAuth auth or first-party/local auth. A working provider integration can still be the wrong product decision.
2. **Check build-time env scope, not just repository env files.** Vite only inlines variables visible to the frontend build process (`VITE_*` in the app's cwd env files or exported shell env). A root `.env` is not automatically loaded when building from a nested `apps/web` directory unless the project explicitly loads it.
3. **Provider UI often needs both a client and a provider wrapper.** If the UI renders only skeleton lines/separators, verify the auth UI package's required CSS import and context provider, not just the page component.
4. **Reverting auth provider changes requires removing build-time env too.** If a temporary `.env.local` was created to enable a hosted auth provider, delete it (or remove the provider variable) before rebuilding, otherwise the deployed bundle may keep choosing the hosted auth path.
5. **Verify the deployed artifact, not only source.** Fetch the public HTML asset names and inspect or render the deployed bundle for expected markers (e.g. local email/password labels present, OAuth provider label absent/present as required).
6. **If the env var keeps leaking across rebuilds, remove the code path entirely.** Unsetting env vars before each build is fragile — a single missed rebuild re-breaks the auth UI. When the project has permanently switched to local auth, remove the provider SDK imports, conditional rendering, and env-gated initialization; hardcode the feature flag to `false`. See `full-stack-feature-implementation/references/vite-rebuild-env-pollution.md` for the full recipe.

## Minimal verification checklist

- Build from the same frontend app directory used in deployment.
- Deploy the new `dist/` to the public static directory.
- Fetch the public login URL with a cache-busting query string.
- Confirm public DOM/text contains the intended auth labels.
- Confirm unintended provider labels are absent.
- Run the focused auth page test when available.
