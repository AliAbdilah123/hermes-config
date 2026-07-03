#!/usr/bin/env python3
"""Collect Discord auto-thread activity for the daily Hermes report.

Reads discord.allowed_channels from this profile's config.yaml on every run.
Outputs compact JSON for an agent to summarize.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

API = "https://discord.com/api/v10"
GUILD_ID = "1497600893833445578"
HERMES_HOME = Path(os.environ.get("HERMES_HOME") or Path.home() / ".hermes/profiles/coder-orchestrator")
CONFIG_PATH = HERMES_HOME / "config.yaml"
WINDOW_HOURS = int(os.environ.get("DISCORD_REPORT_WINDOW_HOURS", "24"))


def token() -> str:
    tok = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
    if tok:
        return tok
    env_path = HERMES_HOME / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("DISCORD_BOT_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("DISCORD_BOT_TOKEN is not set")


def discord(method: str, path: str, params: dict[str, str] | None = None) -> Any:
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, method=method, headers={
        "Authorization": f"Bot {token()}",
        "User-Agent": "Hermes daily Discord thread report",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status == 204:
                return None
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        return {"_error": f"HTTP {e.code}: {body[:300]}", "_path": path}


def allowed_channels() -> list[str]:
    """Tiny YAML reader for discord.allowed_channels; avoids PyYAML dependency."""
    lines = CONFIG_PATH.read_text().splitlines()
    in_discord = False
    in_allowed = False
    ids: list[str] = []
    for raw in lines:
        line = raw.rstrip()
        if line and not line.startswith(" "):
            in_discord = line == "discord:"
            in_allowed = False
            continue
        if not in_discord:
            continue
        stripped = line.strip()
        if stripped.startswith("allowed_channels:"):
            in_allowed = True
            tail = stripped.split(":", 1)[1].strip()
            if tail and tail not in ("''", '""'):
                ids.extend(x.strip().strip('"\'') for x in tail.split(",") if x.strip())
            continue
        if in_allowed:
            if stripped.startswith("- "):
                val = stripped[2:].strip().strip('"\'')
                if val:
                    ids.append(val)
            elif stripped and not stripped.startswith("#"):
                break
    # allowed channel entries may be "parent:thread" topic keys; report both safely.
    out: list[str] = []
    for item in ids:
        for part in item.split(":"):
            part = part.strip()
            if part.isdigit() and part not in out:
                out.append(part)
    return out


def snowflake_after(dt: datetime) -> str:
    discord_epoch_ms = 1420070400000
    ms = int(dt.timestamp() * 1000)
    return str((ms - discord_epoch_ms) << 22)


def channel_name(channel_id: str) -> str:
    ch = discord("GET", f"/channels/{channel_id}")
    if isinstance(ch, dict) and not ch.get("_error"):
        return ch.get("name") or channel_id
    return channel_id


def list_threads(parent_id: str) -> list[dict[str, Any]]:
    threads: dict[str, dict[str, Any]] = {}
    for path in (
        f"/channels/{parent_id}/threads/active",
        f"/channels/{parent_id}/threads/archived/public",
        f"/channels/{parent_id}/threads/archived/private",
    ):
        data = discord("GET", path, {"limit": "100"})
        if isinstance(data, dict) and data.get("threads"):
            for th in data["threads"]:
                threads[th["id"]] = th
    return list(threads.values())


def fetch_messages(channel_id: str, after: str) -> list[dict[str, Any]]:
    msgs: list[dict[str, Any]] = []
    cursor = after
    while True:
        data = discord("GET", f"/channels/{channel_id}/messages", {"limit": "100", "after": cursor})
        if isinstance(data, dict) and data.get("_error"):
            return [{"_error": data["_error"]}]
        if not data:
            break
        batch = list(reversed(data))  # API returns newest first
        msgs.extend(batch)
        cursor = batch[-1]["id"]
        if len(batch) < 100:
            break
        time.sleep(0.35)  # ponytail: simple rate-limit politeness; upgrade if 429s appear.
    return msgs


def simplify_messages(msgs: list[dict[str, Any]]) -> tuple[list[dict[str, str]], dict[str, int]]:
    human: list[dict[str, str]] = []
    counts: dict[str, int] = {}
    for m in msgs:
        if m.get("_error"):
            continue
        a = m.get("author") or {}
        if a.get("bot"):
            continue
        name = a.get("global_name") or a.get("username") or a.get("id") or "unknown"
        counts[name] = counts.get(name, 0) + 1
        content = (m.get("content") or "").replace("\n", " ").strip()
        human.append({
            "time": m.get("timestamp", ""),
            "author": name,
            "content": content[:800],
        })
    return human, counts


def main() -> None:
    since = datetime.now(timezone.utc) - timedelta(hours=WINDOW_HOURS)
    after = snowflake_after(since)
    allowed = allowed_channels()
    report: dict[str, Any] = {
        "guild_id": GUILD_ID,
        "window_start_utc": since.isoformat(),
        "window_end_utc": datetime.now(timezone.utc).isoformat(),
        "allowed_channels_from_config": allowed,
        "threads": [],
        "errors": [],
    }

    for parent in allowed:
        parent_label = channel_name(parent)

        # Always fetch top-level parent channel messages too
        parent_msgs = fetch_messages(parent, after)
        parent_human, parent_counts = simplify_messages(parent_msgs)
        if parent_human:
            report["threads"].append({
                "parent_channel_id": parent,
                "parent_channel_name": parent_label,
                "thread_id": parent,
                "thread_name": parent_label,
                "human_message_count": len(parent_human),
                "human_message_counts_by_author": parent_counts,
                "messages": parent_human,
            })

        threads = list_threads(parent)
        for th in threads:
            msgs = fetch_messages(th["id"], after)
            if msgs and msgs[0].get("_error"):
                report["errors"].append({"thread_id": th["id"], "error": msgs[0]["_error"]})
                continue
            human, counts = simplify_messages(msgs)
            if not human:
                continue
            report["threads"].append({
                "parent_channel_id": parent,
                "parent_channel_name": parent_label,
                "thread_id": th["id"],
                "thread_name": th.get("name") or th["id"],
                "human_message_count": len(human),
                "human_message_counts_by_author": counts,
                "messages": human,
            })

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
