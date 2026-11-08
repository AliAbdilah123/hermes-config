#!/usr/bin/env bash
set -euo pipefail
systemctl --user restart hermes-gateway-coder-orchestrator.service
systemctl --user is-active hermes-gateway-coder-orchestrator.service
