Discord project defaults: #p-socialzen=SocialZen; #p-boilerplate=boilerplate; #p-komuna=Komuna; #p-komuna-old=komuna-old; #p-video-slicer=video-slicer; <#1518958014626005154>=multitenant-auth-saas-boilerplate unless stated otherwise.
§
When implementing a new project, copy the boilerplate project as the base by default unless the user specifies otherwise.
§
For this user's projects, `.env` and `sqlite.db` are placed in each project's directory/root unless specified otherwise.
§
The user's current public project host IP is http://168.110.213.104. Do not use the earlier private/local IP 10.0.0.105 as a public project link.
§
For migration tasks, do not recreate the target project from the boilerplate by default. Treat migration as porting/converting the existing source project in place or into a cloned target while preserving project identity; use boilerplate only as a reference for stack patterns, not as the base, unless the user explicitly asks.
§
For this user, after updating a public PRD/document HTML, publish or provide a versioned/cache-busted URL and verify the public URL contains the specific new text before finalizing; do not rely on a previously shared URL that may be cached.
§
Komuna Vite frontend builds from apps/web, so Vite only auto-loads env files in apps/web; root /home/ubuntu/projects/komuna/.env is not auto-loaded. VITE_NEON_AUTH_URL must be exported or copied into apps/web/.env.local before building, otherwise the deployed login falls back to the basic local email/password page.
§
Komuna login should use the basic SQLite/local email-password flow by default, not Neon Auth or Google OAuth, unless the user explicitly asks to switch auth providers.
§
Discord project default: <#1520812080180232312>=self-flow. Conversations in that channel are about the self-flow project by default unless stated otherwise.