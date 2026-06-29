---
name: messaging-gateway-triage
description: "Triage why a Hermes messaging/gateway agent did not respond: message delivery, allowlists, channel/thread routing, restarts, and session resume state."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, gateway, discord, telegram, slack, troubleshooting, allowlist, routing]
    created_by: agent
---

# Messaging Gateway Triage

Use this skill when a user says a Hermes profile/bot did not respond to a Discord/Telegram/Slack/etc. message, asks why a linked message was ignored, or asks to verify whether a channel/thread is allowed.

## Goal

Determine whether the message reached Hermes, whether it was dropped by platform routing/allowlist/mention policy, whether the agent started but was interrupted, and what concrete action fixes the issue.

## Triage Workflow

1. **Identify the active profile and config path.**
   - Run `hermes config path` or `hermes status --all` from the relevant profile/session.
   - For profile-specific gateways, inspect `~/.hermes/profiles/<profile>/...`, not the default `~/.hermes/...` unless the service is actually using the default profile.

2. **Extract routing IDs from the user’s link/message.**
   - Discord message links have: `https://discord.com/channels/<guild_id>/<channel_or_thread_id>/<message_id>`.
   - Keep all three IDs; the parent channel and thread may differ.
   - For Discord snowflakes, decode the timestamp to compare with logs and config changes.

3. **Check gateway logs for actual ingestion.**
   - Search the active profile’s gateway log for the message ID, channel/thread ID, guild ID, user name, and nearby timestamps.
   - Key distinction:
     - `inbound message` exists → Hermes received it; debug agent execution, model/tool errors, timeout, or send failure.
     - No `inbound message` for that message → platform adapter likely filtered it before agent execution; debug allowlist, mention policy, channel permissions, bot visibility, or restart timing.

4. **Check allowlist and response policy.**
   - Inspect `discord.allowed_channels`, `discord.free_response_channels`, `discord.require_mention`, `discord.thread_require_mention`, `discord.auto_thread`, and equivalent settings for other platforms.
   - For Discord threads, verify whether the config needs the thread ID, the parent channel ID, or a `parent:thread` entry. Existing configs may contain all three styles; compare with nearby working entries.
   - If you change tool/platform config, remember it normally takes a gateway restart or fresh session to become active.

5. **Check interruption/restart state.**
   - Look for `Received SIGTERM`, `Stopping gateway`, `response ready`, `Sending response`, `Scheduled auto-resume`, and `resume_pending` entries.
   - If a restart happened while a turn was running, report that separately from allowlist issues.

6. **Check session metadata when needed.**
   - Search profile session files/state for `origin.chat_id`, `thread_id`, `parent_chat_id`, `guild_id`, and `message_id` to confirm what Hermes believed the conversation target was.

7. **Conclude with evidence and a concrete next step.**
   - State exactly which evidence was found: config entry, inbound log present/absent, response send present/absent, restart timing.
   - If the old message was filtered before ingestion, tell the user to repost/reply now that routing is fixed; Hermes cannot retroactively process a message it never received unless you manually reconstruct and run the request.

## Useful Commands

```bash
# Profile/config/service overview
hermes config path
hermes status --all

# Search active profile and default logs when unsure which service handled it
grep -i "<message_id>\|<channel_id>\|<thread_id>\|allowed\|allowlist" \
  ~/.hermes/profiles/<profile>/logs/gateway.log ~/.hermes/logs/gateway.log 2>/dev/null | tail -100

# Inspect profile config around platform settings
# Prefer read_file in agent sessions; use an editor or yq from shell if available.

# Decode Discord snowflake timestamp
python3 - <<'PY'
import datetime
DISCORD_EPOCH = 1420070400000
for s in ['<message_id>']:
    n = int(s)
    ts = ((n >> 22) + DISCORD_EPOCH) / 1000
    print(s, datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).isoformat())
PY
```

## Pitfalls

- Do not assume the bot ignored a message just because it did not answer. First prove whether the gateway logged an `inbound message`.
- Do not inspect only the default `~/.hermes/logs/gateway.log` when the active agent is a named profile; profile logs may contain the real event.
- Do not treat a channel being present in config now as proof it was allowed at the time of the original message. Compare message timestamp, config edit timing, and gateway restart timing.
- Avoid permanent negative conclusions like “Discord is broken” or “gateway did not work.” Describe the observed routing state and the fix.

## References

- `references/discord-linked-message-nonresponse.md` — compact case note for diagnosing a Discord message link that never appeared as an inbound gateway event.
