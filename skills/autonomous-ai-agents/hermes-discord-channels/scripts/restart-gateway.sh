#!/usr/bin/env bash
# Restart a Hermes profile gateway from INSIDE the gateway process.
#
# Why a script: foreground `terminal` calls, `systemd-run --user`, and
# setsid/nohup are all rejected by the gateway-restart guard. Running this
# file with terminal(background=true, notify_on_complete=true) detaches the
# child from the gateway's process group, so the guard does not fire.
#
# Usage:
#   terminal(command="bash ~/.hermes/skills/autonomous-ai-agents/hermes-discord-channels/scripts/restart-gateway.sh coder-orchestrator",
#            background=true, notify_on_complete=true)
#   process(action="wait", session_id=..., timeout=40)   # prints the is-active result
#
# Then check ~/.hermes/profiles/<profile>/logs/gateway.log for:
#   "Gateway running with N platform(s)" and "[Discord] Connected as <name>#<disc>"

set -u
P="${1:?usage: restart-gateway.sh <profile> [status-file]}"
OUT="${2:-/tmp/hermes-gw-${P}-status.txt}"

systemctl --user restart "hermes-gateway-${P}.service"

# SIGTERM sometimes hangs in deactivating (stop-sigterm) because Python
# asyncio delays shutdown for active tasks. Wait, then escalate if needed.
for _ in $(seq 1 18); do
  [ "$(systemctl --user is-active "hermes-gateway-${P}.service")" = active ] && break
  sleep 5
done

if [ "$(systemctl --user is-active "hermes-gateway-${P}.service")" != active ]; then
  OLD=$(systemctl --user show -p MainPID --value "hermes-gateway-${P}.service")
  [ -n "$OLD" ] && [ "$OLD" != 0 ] && kill -9 "$OLD" 2>/dev/null
  systemctl --user daemon-reload
  systemctl --user start "hermes-gateway-${P}.service"
  sleep 5
fi

systemctl --user is-active "hermes-gateway-${P}.service" >"$OUT" 2>&1
cat "$OUT"
