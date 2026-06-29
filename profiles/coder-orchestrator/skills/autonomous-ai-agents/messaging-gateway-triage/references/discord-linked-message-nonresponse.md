# Discord linked-message non-response triage case

## Situation

User reported that `coder-orchestrator` did not respond to a Discord message link:

```text
https://discord.com/channels/<guild_id>/<channel_or_thread_id>/<message_id>
```

The useful pattern was to prove whether the linked message ever reached the gateway before debugging the agent loop.

## Evidence pattern

1. Decode the Discord message snowflake to get the original message time.
2. Search the active profile gateway log for the message ID and channel/thread ID.
3. Compare with nearby `inbound message`, `response ready`, `Sending response`, and restart lines.
4. Inspect the active profile config for `discord.allowed_channels` and thread/parent entries.
5. Search session metadata for `origin.parent_chat_id`, `thread_id`, and `message_id` if routing is ambiguous.

## Interpretation used

- No `inbound message` line for the linked message ID means the agent did not receive the message; the likely causes are adapter filtering, channel/thread allowlist state, mention policy, or bot visibility/permissions.
- If the channel appears in `allowed_channels` now, still check whether that entry was added after the linked message and whether the gateway restarted afterward.
- A later user message asking why the bot did not respond may appear as inbound in a different thread; do not confuse that with receipt of the original linked message.

## User-facing conclusion format

Keep it short and evidence-based:

```text
I checked the gateway logs and config.

What happened:
- The linked message timestamp was <time>.
- There is/no `inbound message` entry for that message ID.
- The linked channel/thread is/is not currently in `discord.allowed_channels`.
- The gateway was/was not restarted after the relevant config change.

Likely cause: <routing/allowlist/restart explanation>.
Next step: <repost/reply now, add channel, restart gateway, or inspect send failure>.
```
