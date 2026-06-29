Keep an nginx-level troubleshooting checklist up to date under a reusable `nginx` skill in `~/.hermes/skills/nginx/SKILL.md`, with references under `references/config.md`.
§
Hermes multi-profile Discord channel routing: whitelist config is in $HERMES_HOME/profiles/<name>/config.yaml not the main config; both runtime config at /home/ubuntu/.hermes/profiles/ and source config at /home/ubuntu/hermes-config/profiles/ should be kept in sync; restart profile gateway with systemctl --user restart hermes-gateway-<profile>.service — hermes gateway restart from inside gateway is blocked; SIGTERM can hang systemd restart — kill -9 old PID then start if needed.
§
Hermes dashboard may fail silently if web/dist is missing; run npm install && npm run build in hermes-agent/web before starting.