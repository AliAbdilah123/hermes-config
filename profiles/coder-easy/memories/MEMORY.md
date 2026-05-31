Public IP: 168.110.196.49
§
Local verification for completed projects: backend API at 127.0.0.1:8080 before nginx; public URL already works (http://168.110.196.49/projects/demo/).
§
Default project conventions unless overridden: frontend = TypeScript + React via Vite, backend = Go HTTP server, database = SQLite, routes at /api/v1/* plus /projects/<projectName>/api/v1/*, public access at http://168.110.196.49/projects/<projectName> via nginx.
§
Environment: Oracle Linux 9 with nginx 1.20.1, SELinux Enforcing by default, runs as 'nginx' user. Home dirs (/home/opc) default to 700/drwx------. To expose local projects via nginx: either copy builds under /usr/share/nginx/html/<project>/ owned by nginx:nginx, or grant traverse+read to the source path. For backend proxies with SELinux enforcing: setsebool -P httpd_can_network_connect on.
§
Default project conventions (override only when asked): TypeScript + React via Vite on the frontend, Go HTTP server backend with port 8080, SQLite database, public exposure at http://168.110.196.49/projects/<projectName> via nginx.
§
Public access in this environment is http://168.110.196.49/projects/<projectName> via nginx. Project files should be owned by nginx:nginx and placed under /usr/share/nginx/html/projects/<projectName>.
§
AI Ops Lite scaffolding complete: repo https://github.com/AliAbdilah123/aiops-lite with PRD, OpenAPI, PR review workflow placeholder, and `github-pr-orchestrator` skill.
§
Hermes config auto-backups are enabled to https://github.com/AliAbdilah123/hermes-config.git via ~/.hermes/scripts/backup-github.sh and cron job 'hermes-config-backup' (every 1h). Remote also uses SSH (git@github.com:…). Repo state is in ~/.hermes-backups/hermes-config. Key excluded paths: node, node_modules, __pycache__, *.pyc, *.jar, logs, state.db*, Kanban.gz, .env, .auth.