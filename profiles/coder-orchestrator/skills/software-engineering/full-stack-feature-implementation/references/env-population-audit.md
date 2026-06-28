# Env population audit workflow

Use when asked to populate an existing project `.env` with variables the app references but the env files do not yet provide.

## Safe approach

1. **Do not print secret-bearing values.** Inspect env files key-only: parse left-hand side names and report only keys added/missing.
2. **Collect app references from source, not build artifacts.** Search backend config loaders (`os.Getenv`, `os.LookupEnv`, local `env(...)` helpers, `firstEnv(...)`) and frontend env access (`import.meta.env.*`, `process.env.*`). Exclude `node_modules`, `dist`, `.git`, data directories, and generated assets.
3. **Check all env surfaces, not just the root file.** For Vite apps, keys used by frontend code may need to exist in `apps/frontend/.env.development` and `.env.production`; if the dev script loads root `.env` into the frontend process, also add root `VITE_*` keys where appropriate.
4. **Prefer safe placeholders for optional integrations.** Add empty values plus comments for optional keys (for example analytics keys), and keep non-secret defaults where the code already has a documented default (for example a PostHog host). Do not invent provider credentials.
5. **Include accepted aliases.** If backend config accepts multiple alias names (`FRONTEND_BASE_URL`/`FRONTEND_URL`/`ALLOWED_ORIGIN`, `META_APP_ID`/`FACEBOOK_APP_ID`/legacy `INSTAGRAM_APP_ID`), add missing alias keys as empty/commented entries so future deploys do not appear under-provisioned.
6. **Verify with a key audit and builds/tests.** After writing env files, rerun the key audit to confirm no referenced env names are missing, then run the project’s normal frontend typecheck/build and backend tests.

## Reporting

- List only env key names added, never values.
- Separate optional placeholders from required runtime secrets when possible.
- Mention unrelated pre-existing git changes without touching or claiming them.
