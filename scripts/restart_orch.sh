#!/bin/bash
# Triggered by proxy: restarts the orchestrator gateway profile service
unit="hermes-gateway-coder-orchestrator"
svc="$unit.service"
systemctl --user restart "$svc"
sleep 4
systemctl --user is-active "$svc"
