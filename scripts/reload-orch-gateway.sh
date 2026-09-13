#!/bin/bash
systemctl --user restart hermes-gateway-coder-orchestrator.service
sleep 10
systemctl --user is-active hermes-gateway-coder-orchestrator.service > /tmp/gw-orch-status.txt 2>&1
