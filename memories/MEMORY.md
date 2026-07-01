Keep an nginx-level troubleshooting checklist up to date under a reusable `nginx` skill in `~/.hermes/skills/nginx/SKILL.md`, with references under `references/config.md`.
§
Hermes multi-profile Discord channel routing: whitelist config is in $HERMES_HOME/profiles/<name>/config.yaml not the main config; both runtime config at /home/ubuntu/.hermes/profiles/ and source config at /home/ubuntu/hermes-config/profiles/ should be kept in sync; restart profile gateway with systemctl --user restart hermes-gateway-<profile>.service — hermes gateway restart from inside gateway is blocked; SIGTERM can hang systemd restart — kill -9 old PID then start if needed.
§
Hermes dashboard may fail silently if web/dist is missing; run npm install && npm run build in hermes-agent/web before starting.
§
9router is managed by a user-level systemd service at /home/ubuntu/.config/systemd/user/9router.service; runs ubuntu-owned node /home/ubuntu/.local/bin/9router, binds port 20128. Do NOT use Group= in user systemd units (status=216/GROUP failure).
§
Go+React projects deployed under nginx `/projects/<name>/` require: build frontend, copy `dist/` to `/var/www/html/projects/<name>/`, update Go `serveReact` path, add nginx proxy + alias blocks inside existing server config.
§
User systemd services must NOT include `User=` nor `Group=`; user manager already runs as the owning user and re-setting groups triggers `Failed to determine supplementary groups` / `status=216/GROUP`.
§
Project `system` renamed/moved to `/home/ubuntu/projects/server-monitor/`, backend built, frontend built, nginx config added, systemd user unit created, verified at `http://168.110.213.104/projects/server-monitor/`.
§
This host runs nginx with config at /etc/nginx/projects/default.conf (single server block). User-level systemd services live at /home/ubuntu/.config/systemd/user/.