Discord project defaults: #p-socialzen=SocialZen; #p-boilerplate=boilerplate; #p-komuna=Komuna; #p-komuna-old=komuna-old; #p-video-slicer=video-slicer; <#1518958014626005154>=multitenant-auth-saas-boilerplate unless stated otherwise.
§
Boilerplate: /home/ubuntu/projects/boilerplate/. Vite+React+Tailwind v4, Go API :8098. SPA at /projects/boilerplate/. Deploy: pnpm build → sudo rsync -a --delete dist/ → chown www-data:www-data. Branch: feat/multi-tenant. Copy as base for new projects.
§
For this user's projects, `.env` and `sqlite.db` are placed in each project's directory/root unless specified otherwise.
§
Public host IP 168.110.213.104. HTTP :80, HTTPS :443 (self-signed /etc/nginx/ssl/). Certbot installed. OCI Security List must allow new ports (cannot be done from terminal). See nginx-server-admin skill.
§
For migrations, don't recreate from boilerplate by default; port/convert the source project in place or into a clone, preserving identity. Use boilerplate only as a pattern reference unless user says otherwise.
§
After updating public PRD/document HTML, provide cache-busted URL and verify live content contains new text before finalizing.
§
Komuna: komuna.ahsanworks.com. Go API :8095, local email/password auth. Vite from apps/web. Seed: delete sqlite.db to re-seed. NEVER simplify DB when migrating — port full relational schema as-is.
§
<#1520812080180232312>=self-flow. Local Go+SQLite (port 8096, JSON-state-in-SQLite, local email/password auth, /projects/self-flow/). Old Node.js in packages/be-serverless+be-services+db. Go API production-hardened 2026-06-30.
§
SocialZen: /projects/socialzen/, socialzen.ahsanworks.com. systemd socialzen.service, env /home/ubuntu/socialzen/.env, Go apps/backend-go/, ADDR=:8089. Deploy Go: stop service→cp binary→start. Health: /api/health on :8089.
§
Tailwind: cn()/tailwind-merge doesn't merge different breakpoint prefixes. sm:max-w-sm in component defaults NOT overridden by max-w-4xl; use sm:max-w-4xl max-w-[calc(100%-2rem)].