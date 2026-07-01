Discord project defaults: #p-socialzen=SocialZen; #p-boilerplate=boilerplate; #p-komuna=Komuna; #p-komuna-old=komuna-old; #p-video-slicer=video-slicer; <#1518958014626005154>=multitenant-auth-saas-boilerplate unless stated otherwise.
§
When implementing a new project, copy the boilerplate project as the base by default unless the user specifies otherwise.
§
For this user's projects, `.env` and `sqlite.db` are placed in each project's directory/root unless specified otherwise.
§
Public host IP 168.110.213.104. HTTP :80, HTTPS :443 (self-signed /etc/nginx/ssl/). Certbot installed. OCI Security List must allow new ports (cannot be done from terminal). See nginx-server-admin skill.
§
For migrations, don't recreate from boilerplate by default; port/convert the source project in place or into a clone, preserving identity. Use boilerplate only as a pattern reference unless user says otherwise.
§
For this user, after updating a public PRD/document HTML, publish or provide a versioned/cache-busted URL and verify the public URL contains the specific new text before finalizing; do not rely on a previously shared URL that may be cached.
§
Komuna login should use the basic SQLite/local email-password flow by default, not Neon Auth or Google OAuth, unless the user explicitly asks to switch auth providers.
§
Discord project default: <#1520812080180232312>=self-flow. Self-flow backend is local Go+SQLite (api/v1/main.go, port 8096, JSON-state-in-SQLite, local email/password auth, deployed at /projects/self-flow/). Previous Node.js implementation preserved in packages/be-serverless+be-services+db. Go API production-hardened 2026-06-30.
§
SocialZen: IP path /projects/socialzen/. Domain socialzen.ahsanworks.com pending (DNS+certbot). systemd socialzen.service, env /home/ubuntu/socialzen/.env, Go apps/backend-go/, ADDR=:8089 (8080=fnb-pos). Health: /api/health on :8089.
§
Komuna Vite builds from apps/web; root .env not auto-loaded. For local basic auth, VITE_NEON_AUTH_URL must NOT be set during build — if it leaks, auth page flips to broken Neon widget.