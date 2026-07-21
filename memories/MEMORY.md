Keep nginx troubleshooting checklist inside `~/.hermes/skills/nginx/SKILL.md` with references in `references/config.md`.
§
Hermes multi-profile Discord channel routing: whitelist config is in $HERMES_HOME/profiles/<name>/config.yaml not the main config; both runtime config at /home/ubuntu/.hermes/profiles/ and source config at /home/ubuntu/hermes-config/profiles/ should be kept in sync. Use `discord.channel_prompts` to set default per-channel/topic context; keys are channel IDs or `channel:thread` pairs. Restart profile gateway with systemctl --user restart hermes-gateway-<profile>.service — if SIGTERM hangs showing stop-sigterm, kill -9 old PID then start.
§
Hermes dashboard may appear to error when `/api/*` returns 401 from bare curl; that is expected because auth uses an ephemeral session token injected into `index.html`. Verify dashboard health with root `/` (expect 200 HTML) or pass `Authorization: Bearer <token>` where token is from the injected `window.__HERMES_SESSION_TOKEN__`.
§
9router is managed by a user-level systemd service at /home/ubuntu/.config/systemd/user/9router.service; runs ubuntu-owned node /home/ubuntu/.local/bin/9router, binds port 20128. Do NOT use Group= in user systemd units (status=216/GROUP failure).
§
Go+React projects deployed under nginx `/projects/<name>/` require: build frontend, copy `dist/` to `/var/www/html/projects/<name>/`, update Go `serveReact` path, add nginx proxy + alias blocks inside existing server config.
§
User systemd services must NOT include `User=` nor `Group=`; user manager already runs as the owning user and re-setting groups triggers `Failed to determine supplementary groups` / `status=216/GROUP`.
§
This host runs nginx with config at /etc/nginx/projects/default.conf (single server block). User-level systemd services live at /home/ubuntu/.config/systemd/user/.
§
Default project: Paragentix at /home/ubuntu/projects/paragentix. Use terminal directly with that workdir for all shell work; delegated shell must request terminal explicitly. Job cards: truncate task to ~15 words or ~60 chars with '...' when longer; these are just notes, not a summary of work done.