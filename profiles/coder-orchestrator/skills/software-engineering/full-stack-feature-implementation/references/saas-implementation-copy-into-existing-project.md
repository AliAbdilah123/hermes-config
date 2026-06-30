# Copying a SaaS implementation into an existing project while preserving target conventions

Use when the user asks to copy/port the implementation of an existing SaaS boilerplate into another local project, especially when the target has different layout conventions.

## Pattern

1. Identify source and target explicitly from local project directories and chat/channel defaults.
2. Inspect both layouts before copying. Decide which target conventions must stay stable:
   - project root `.env` and `sqlite.db`
   - existing backend entrypoint path/service name
   - public subpath `/projects/<slug>/`
   - frontend source location and Vite base path
3. Copy implementation, not secrets or runtime artifacts:
   - exclude `.git`, `node_modules`, `dist`, `.env`, and live DB files
   - copy docs/tests/migrations where they define behavior
4. Adapt paths after copy:
   - default DB path should use project-root `sqlite.db` unless user says otherwise
   - Vite `base` must match the deployed subpath
   - frontend API helper should resolve through the same subpath when deployed
   - backend command should live at the target's conventional entrypoint
5. Keep deployment naming target-specific:
   - binary/service names should match the target slug
   - systemd `EnvironmentFile=-/path/to/project/.env` is preferred over embedding secrets
   - nginx should proxy `/projects/<slug>/api/v1/` to the local API and serve SPA assets from `/var/www/html/projects/<slug>/`
6. Verify at three layers:
   - frontend build/tests
   - backend tests/build
   - public SPA index, public JS asset, public health/API response, and bundle markers

## Pitfalls

- Do not copy source `.env` or DBs into the target.
- Do not leave source project service names, Vite bases, public paths, or DB paths in the target.
- **Hardcoded service-name strings in API response bodies are easy to miss.** Health endpoints (`/api/v1/health`), config endpoints, and error messages often contain a literal source-project name string (e.g. `"service":"multitenant-auth-saas-boilerplate"`). After copying, grep for the source project name across backend source and update every user-visible identifier to the target project name. A stale service name in a health response will make the user (or you) question whether the correct deployment is live, even when nginx, systemd, and asset hashes all prove otherwise.
- A systemd service may report active immediately before its socket is ready; if the first local curl races and fails, check status/journal and retry after the service logs its listen address.
- For Tailwind v4/Vite apps, warnings from CSS minifiers about `@theme`/`@utility` may be noisy but not fatal if the build exits 0 and deployed CSS renders; do not treat them as a blocker without visual/runtime evidence.
