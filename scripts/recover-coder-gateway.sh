#!/usr/bin/env bash
set -euo pipefail
unit=hermes-gateway-coder-orchestrator.service
pid=$(systemctl --user show "$unit" -p MainPID --value)
if [ "${pid:-0}" -gt 0 ]; then kill -9 "$pid" || true; fi
sleep 2
systemctl --user daemon-reload
systemctl --user start "$unit"
sleep 8
systemctl --user is-active "$unit"
