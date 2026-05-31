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
- Let all other requested paths serve the built React app from `frontend/dist`.
- Listen on `:8080` by default.

## Frontend requirements
- Set `vite.config.ts` base to `/projects/<projectName>/` so assets resolve after deploy.
- Do not use `root` in nginx when alias exists; avoid path doubling.

## Nginx behavior
- Expose the React build under `/projects/<projectName>/`.
- Proxy `/api/v1/` and `/wiki/` to the Go backend at `http://127.0.0.1:8080`.
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

## References
- See `references/demo.md` for concrete nginx snippets and the final working config.
- See `references/permissions.md` for the SELinux permission fix and why copying the build to `/usr/share/nginx/html` works.
