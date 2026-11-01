#!/usr/bin/env bash
set -euo pipefail
systemctl --user restart hermes-gateway-researcher.service
systemctl --user is-active --quiet hermes-gateway-researcher.service
systemctl --user show hermes-gateway-researcher.service -p ActiveState -p SubState -p MainPID
