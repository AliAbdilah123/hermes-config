# Auto-thread daily Discord reports

## Context

A custom bot may create one thread per message. In that setup, useful daily reporting should summarize thread activity, not only parent-channel messages.

## Runtime config pattern

When the user says to use the coding-orchestrator allowed channels, read this profile file on every run:

```text
~/.hermes/profiles/coder-orchestrator/config.yaml
  discord:
    allowed_channels:
      - 'channel_id'
      - 'parent_id:thread_id'
```

Treat `parent_id:thread_id` entries defensively: split on `:` and consider both numeric IDs. Some entries may point at topics/threads rather than parent channels.

## Collector pattern

Use stdlib `urllib.request` and JSON output; avoid extra dependencies. Read `DISCORD_BOT_TOKEN` from the environment, falling back to the profile `.env` if necessary.

For each allowed parent channel:

1. Fetch threads:
   - `/channels/{parent}/threads/active`
   - `/channels/{parent}/threads/archived/public`
   - `/channels/{parent}/threads/archived/private`
2. For each thread, fetch messages after a snowflake derived from the report window start:
   - `/channels/{thread_id}/messages?limit=100&after={snowflake}`
3. Reverse each returned batch because Discord returns newest-first.
4. Exclude `author.bot` when the user asks for human-only reporting.
5. Emit compact per-thread objects:

```json
{
  "guild_id": "...",
  "window_start_utc": "...",
  "window_end_utc": "...",
  "allowed_channels_from_config": ["..."],
  "threads": [
    {
      "parent_channel_id": "...",
      "parent_channel_name": "...",
      "thread_id": "...",
      "thread_name": "...",
      "human_message_count": 3,
      "human_message_counts_by_author": {"Name": 3},
      "messages": [
        {"time": "ISO", "author": "Name", "content": "trimmed content"}
      ]
    }
  ],
  "errors": []
}
```

If a channel has no listed threads, still try fetching direct messages for that ID. This covers allowed entries that are already thread IDs.

## Cron pattern

Create a recurring cron with:

- `script`: just the relative script filename, not an absolute path.
- `workdir`: directory containing the script if needed.
- `deliver: origin` for the current DM/channel.
- Prompt: summarize only the injected script output; include total human messages, active threads, per-person counts with time spans, and topic summaries grouped by thread.

Example schedule:

```text
0 9 * * *
```

Check `next_run_at` after creation. Hermes may display the next run in UTC, so report the timezone explicitly to the user.

## Verification checklist

- Collector runs and outputs valid JSON.
- Reported allowed-channel count matches config expectation.
- Errors list is empty or clearly explained.
- Manual run shows active thread count and human message count.
- Cron job exists, is enabled, and has the intended delivery target.
