# Legacy skill package: `default-web-stack`

This file preserves the former `default-web-stack` SKILL.md after consolidation into `web-app-delivery`. Relative support-file links have been rewritten to the re-homed files under `web-app-delivery`.

---

---
name: default-web-stack
title: Default Web Stack
description: Frontend React + TypeScript, Go backend at /api/v1/*, SQLite, served under /projects/<projectName> via nginx.
---

# Default Web Stack

Use this skill when the user asks you to build or serve a web project and does not provide a tech stack.

## Project shape
- frontend: TypeScript + React with Vite
- backend: Go
- db: sqlite via modernc.org/sqlite
- public path: `<publicIP>/projects/<projectName>`

## Backend contract
- Keep APIs under `/api/v1/*`.
- Go serves API only; it does not serve the React build in normal deployments.
- Listen on `:8080` by default.
- Do not run a React/Vite dev server for deployed or verified builds unless explicitly requested.

## Frontend requirements
- Set `vite.config.ts` base to `/projects/<projectName>/` so assets resolve after deploy.
- Treat Vite as a build tool only for normal delivery: `npm run build`, then nginx serves `frontend/dist`.

## Nginx behavior
- Serve the compiled React build under `/projects/<projectName>/` from nginx.
- Proxy API paths (`/api/v1/` and `/projects/<projectName>/api/v1/` when needed) to the Go backend at `http://127.0.0.1:8080`.
- Use `alias` for the frontend path. Do not use `root` plus `try_files` for `/projects/<projectName>/`; it causes path doubling.
- After `nginx -t`, use `sudo nginx -s reload` and verify public and local URLs before declaring success.

## Verification order
1. Backend direct: `http://127.0.0.1:8080/api/v1/hello`
2. Nginx API: `http://127.0.0.1/api/v1/hello`
3. Frontend root: `http://127.0.0.1/projects/<projectName>/`
4. Public frontend: `http://<publicIP>/projects/<projectName>/`

## Stack rule
- Once TS/React + Go + SQLite is selected, keep it unless the user explicitly changes it. Do not silently switch backend language, replace the frontend with plain HTML/JS, or introduce unaudited stack substitutions.

## Known pitfalls
- Stack substitution is a last resort and must be user-approved explicitly.
- SELinux can prevent the nginx worker from reading user home directories. Copy the built frontend into `/usr/share/nginx/html/projects/<projectName>/` and `chown -R nginx:nginx` that path.
- Do not use `go:embed all:..` patterns; embed only concrete directories inside the module.
- Multiple server blocks with `server_name _;` on the same `listen 80` cause harmless ignored warnings but can hide config issues. Keep one default server.
- If another project already owns `/api/v1/` or port `8080`, do not disrupt it. Make the Go service read `PORT` from the environment, run it on a free project-specific port, and proxy only `/projects/<projectName>/api/v1/` to that port. The frontend should choose `/projects/<projectName>/api/v1` when served under the project path and `/api/v1` only for local/dev root serving.
- When returning Go structs to a TypeScript frontend, add explicit camelCase JSON tags (`json:"programId"`, `json:"expiredAt"`, etc.). Exported Go fields otherwise serialize as PascalCase (`ProgramID`, `ExpiredAt`), which silently breaks frontend code typed for camelCase API contracts.
- On hosts where nginx already has a default `server { ... location /projects/ ... }` catch-all, add the new project-specific `location /projects/<projectName>/...` blocks inside that existing default server before the catch-all. A standalone include with only `location` blocks is invalid, and a second default server may be ignored depending on include order.
- Public-IP curl from the same instance can fail due to hairpin routing even when the app is reachable externally. Do not treat that alone as a failed deployment; verify local nginx (`127.0.0.1/projects/<projectName>/`), proxied API, assets, and service health, then ask the user to open the public URL if internal public-IP curl times out.

## References
- See `references/default-web-stack-demo.md` for concrete nginx snippets and the final working config.
- See `references/permissions.md` for the SELinux permission fix and why copying the build to `/usr/share/nginx/html` works.
