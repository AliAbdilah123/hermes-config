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
PRD/docs HTML: deploy to /usr/share/nginx/html/prds/ (nginx /prd/ alias), set 644. Verify with curl -sI http://localhost/prd/name.
§
Komuna: komuna.ahsanworks.com. Go API :8095, auth (PW: salt:sha256×120K), service komuna-api, binary api/server. DB sqlite.db (WAL, relational schema — NOT old JSON blob). NEVER rm sqlite.db — seed additively with INSERT/DELETE + PRAGMA foreign_keys=OFF. Seed scripts: /tmp/komuna-reseed-v2.py & /tmp/komuna-fill.py. Rebuild: cd api/v1 && CGO_ENABLED=1 go build -o ../server .
§
SocialZen: /home/ubuntu/socialzen/, socialzen.ahsanworks.com. Go apps/backend-go/, ADDR=:8089. Service WorkingDirectory=/opt/socialzen. Deploy Go: go build→stop→cp→start. Frontend: pnpm build→rsync /var/www/socialzen.
§
Tailwind: cn()/tailwind-merge doesn't merge different breakpoint prefixes. sm:max-w-sm in component defaults NOT overridden by max-w-4xl; use sm:max-w-4xl max-w-[calc(100%-2rem)].
§
self-flow: /projects/self-flow/, selfflow.ahsanworks.com. Go+SQLite :8096, JSON-state-in-SQLite, email/password auth. Old Node.js in packages/be-serverless+be-services+db. Go API prod-hardened 2026-06-30. Primary URL: selfflow.ahsanworks.com.