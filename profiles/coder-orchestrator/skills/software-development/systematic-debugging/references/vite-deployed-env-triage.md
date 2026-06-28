# Vite deployed-env triage

Use when a Vite/React production page takes the wrong branch because an `import.meta.env.VITE_*` value appears missing after deployment, especially in monorepos.

## Root cause pattern

Vite only auto-loads env files from the app's Vite project root (`envDir`, default = current Vite root), not necessarily the repository root. In a monorepo where the build runs from `apps/web`, a root-level `.env` may contain the correct `VITE_*` values but the compiled production bundle can still inline `undefined`.

Example symptom: login route renders a local/basic fallback instead of provider UI because:

```ts
const providerUrl = import.meta.env.VITE_PROVIDER_URL?.trim()
const isProviderConfigured = Boolean(providerUrl)
```

compiled as an undefined value in the deployed JS.

## Investigation checklist

1. Inspect the source branch that chooses provider UI vs fallback.
2. Check the build working directory and Vite root/envDir.
3. Compare env files in the repo root vs the app root (`apps/web/.env.local`, `apps/web/.env`, etc.).
4. Inspect the deployed JS bundle directly, not just source files:
   - Look for the provider domain or expected literal.
   - Look for `(void 0)?.trim` or similar inlined-undefined patterns.
   - Look for fallback-only constants/tokens that prove the wrong branch is compiled.
5. Rebuild with the `VITE_*` values available to Vite from the correct app root or exported in the build environment.
6. Publish the rebuilt `dist/` and verify the public HTML references the new hashed asset.
7. Fetch the public JS asset and verify it contains the expected provider literal and no inlined-undefined env expression.

## Fix options

- Put frontend env in the app root, e.g. `apps/web/.env.local` (usually gitignored).
- Export env vars in the deployment/build command.
- Configure Vite `envDir` intentionally if the project wants root-level env loading.

## Verification example

```bash
npm run build
rsync -a --delete apps/web/dist/ /var/www/html/projects/<app>/
asset=$(curl -fsS 'http://host/projects/<app>/auth/sign-in' | grep -o 'assets/index-[^" ]*\.js' | head -1)
curl -fsS "http://host/projects/<app>/$asset" | python3 -c "import sys; s=sys.stdin.read(); print('provider-domain' in s, '(void 0)?.trim' in s)"
```

For user-facing verification, prefer a cache-busted URL after deploy because browsers may still have the old hashed HTML/JS cached.
