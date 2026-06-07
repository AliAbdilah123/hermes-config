Public IP: 168.110.196.49
§
Local verification for completed projects: backend API at 127.0.0.1:8080 before nginx; public URL already works (http://168.110.196.49/projects/demo/).
§
Default stack unless overridden: React+TS built by Vite and served from frontend/dist by nginx (no React dev server for deploy/verify), Go API backend, SQLite, /api/v1/* routes, public at http://168.110.196.49/projects/<projectName>.
§
Environment for this profile: Ubuntu with nginx 1.24.0 running as www-data. Main config /etc/nginx/nginx.conf includes /etc/nginx/projects/*.conf; default root is /var/www/html/projects. Public PRDs are served from /var/www/html/prds via /prds/ alias.
§
Public access in this environment is http://168.110.196.49/projects/<projectName> via nginx. Project files should be owned by nginx:nginx and placed under /usr/share/nginx/html/projects/<projectName>.
§
AI Ops Lite scaffolding complete: repo https://github.com/AliAbdilah123/aiops-lite with PRD, OpenAPI, PR review workflow placeholder, and `github-pr-orchestrator` skill.
§
Hermes config auto-backups are enabled to https://github.com/AliAbdilah123/hermes-config.git via ~/.hermes/scripts/backup-github.sh and cron job 'hermes-config-backup' (every 1h). Remote also uses SSH (git@github.com:…). Repo state is in ~/.hermes-backups/hermes-config. Key excluded paths: node, node_modules, __pycache__, *.pyc, *.jar, logs, state.db*, Kanban.gz, .env, .auth.
§
ARM64 headless browser path on this host: /usr/lib64/chromium-browser/headless_shell from chromium-headless RPM. Use with flags like `--no-sandbox --disable-gpu --virtual-time-budget=5000 --dump-dom` or `--screenshot=/tmp/file.png`. agent-browser config is /home/opc/.agent-browser/config.json with executable_path set to that binary.
§
Coding projects should be created and managed under ~/projects.