#p-delegate=delegate; #p-boilerplate=boilerplate
§
WorkingDirectory /opt/socialzen. Frontend dist deploys to /var/www/html/projects/socialzen/ (nginx alias), NOT /var/www/socialzen/. Cloudflare fronts socialzen.ahsanworks.com with 4-hour cache.
§
For this user's projects, `.env` and `sqlite.db` are placed in each project's directory/root unless specified otherwise.
§
Public host IP 168.110.213.104. HTTP :80, HTTPS :443 (self-signed /etc/nginx/ssl/). Certbot installed. OCI Security List must allow new ports (cannot be done from terminal). See nginx-server-admin skill.
§
For migrations, don't recreate from boilerplate by default; port/convert the source project in place or into a clone, preserving identity. Use boilerplate only as a pattern reference unless user says otherwise.
§
PRD/docs HTML: deploy to /usr/share/nginx/html/prds/ (nginx /prd/ alias), set 644. Verify with curl -sI http://localhost/prd/name.
§
When implementing a new project, start from scratch — copy or use the boilerplate project as a clean slate unless the user explicitly specifies otherwise. Do not try to retrofit or evolve an existing unrelated project into the new one.
§
Discord #p-komuna channel = Komuna project at /home/ubuntu/projects/komuna/. Discord #p-socialzen = SocialZen project at /home/ubuntu/socialzen/. When user asks about a bug or feature in a project-prefixed channel, default to that project — don't guess or cross-load skills from other projects.
§
Channel context is the primary signal for project selection. #p-komuna = Komuna project, #p-socialzen = SocialZen. Before doing any work, always verify: (1) what channel/thread is this in, (2) which project does that channel map to, (3) load the correct project skill. Do NOT default to the most recently used project.