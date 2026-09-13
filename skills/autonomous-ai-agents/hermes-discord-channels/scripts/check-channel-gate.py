#!/usr/bin/env python3
"""Verify a Discord channel/thread will actually pass the ingress gate.

Extracts the real ``_discord_channel_keys_from_channel`` from the adapter and
runs it against the real profile config, so it proves the *code path* admits
the target — not just that the ID is somewhere in a YAML list.

Usage:
    ~/.hermes/hermes-agent/venv/bin/python check-channel-gate.py <profile> <channel_id>

Exit code 0 + "INGRESS ADMITTED: True" means the bot will respond once the
gateway has been restarted with that config.
"""
import os
import sys
import textwrap

import yaml

ADAPTER = "/home/ubuntu/.hermes/hermes-agent/plugins/platforms/discord/adapter.py"


class Channel:
    def __init__(self, cid, name, parent_id=None, parent=None):
        self.id, self.name, self.parent_id, self.parent = cid, name, parent_id, parent


def load_channel_keys():
    """Return the adapter's channel-key builder, unbound, as a plain callable."""
    src = open(ADAPTER).read()
    body = src[
        src.index("    def _discord_channel_keys_from_channel("):
        src.index("    def _discord_thread_require_mention(")
    ]
    ns = {}
    exec("from typing import Any, Optional\n" + textwrap.dedent(body).replace("self.", "s."), ns)
    return ns["_discord_channel_keys_from_channel"]


def main() -> int:
    profile, channel_id = sys.argv[1], str(sys.argv[2])
    cfg = yaml.safe_load(open(f"/home/ubuntu/.hermes/profiles/{profile}/config.yaml"))
    discord_cfg = cfg["discord"]
    allowed = {str(v).strip() for v in discord_cfg["allowed_channels"]}

    keys = load_channel_keys()(None, Channel(channel_id, "<target>"))
    matched = keys & allowed
    admitted = "*" in allowed or bool(matched)

    print("channel_keys   :", sorted(str(k) for k in keys))
    print("matched entry  :", sorted(matched) or "(none)")
    print("require_mention:", discord_cfg.get("require_mention"))
    print("INGRESS ADMITTED:", admitted)
    return 0 if admitted else 1


if __name__ == "__main__":
    raise SystemExit(main())
