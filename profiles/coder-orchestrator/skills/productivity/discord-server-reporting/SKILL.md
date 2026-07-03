---
name: discord-server-reporting
description: "Build and operate scheduled Discord server activity reports, especially thread-heavy servers using Hermes cron and Discord REST APIs."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [discord, reporting, cron, threads, daily-summary]
    related_skills: [hermes-agent]
---

# Discord Server Reporting

## When to use

Use this skill when the user asks for recurring summaries/reports of a Discord server, channel, forum, or thread-heavy workflow. Especially relevant when a custom bot auto-creates threads per message and the desired report is based on thread activity rather than flat channel history.

## Core workflow

1. **Confirm report scope**
   - Guild/server ID.
   - Parent channel source: explicit channel IDs, Hermes `discord.allowed_channels`, or another config key.
   - Reporting window and timezone.
   - Delivery target: current DM/channel (`deliver: origin`), another platform target, or file.
   - Content rules: include/exclude bots, message counts, topic summaries, action items, open questions.

2. **Use a script for data collection**
   - Keep cron prompt focused on summarization.
   - Script should fetch raw Discord activity and emit compact JSON.
   - Read configurable channel lists at runtime rather than baking IDs into the cron prompt when the user wants reports to follow config changes.

3. **For auto-thread servers, summarize threads, not just channels**
   - For each parent channel, query:
     - `GET /channels/{channel_id}/threads/active`
     - `GET /channels/{channel_id}/threads/archived/public`
     - `GET /channels/{channel_id}/threads/archived/private` when permitted
     - `GET /channels/{thread_id}/messages`
   - Also handle cases where an allowed channel entry is already a thread ID.

4. **Filter and shape data before the agent sees it**
   - Exclude bot authors if requested.
   - Group messages by thread.
   - Preserve timestamps, author display names, counts by author, parent channel/thread names, and trimmed message content.
   - Avoid dumping unnecessary Discord objects into the model context.

5. **Create a Hermes cron job**
   - Use the script field for collection.
   - Use a self-contained prompt that treats script output as the only source of activity.
   - Use `deliver: origin` for reports back to the current DM/thread unless the user requests another destination.
   - Set `enabled_toolsets` narrowly, usually `['terminal']` or no tools if the script output is sufficient.

6. **Verify before finalizing**
   - Run the collector once manually and report counts: allowed channels, active threads, human messages, errors.
   - Trigger the cron once if appropriate so the user sees a test report on the next scheduler tick.
   - Mention scheduler timezone explicitly; cron schedules are interpreted by Hermes/scheduler timezone and may show as UTC in `next_run_at`.

## Minimal report format

```md
# Daily Discord Auto-Thread Summary — YYYY-MM-DD

## Overview
- Active threads: N
- Human messages: N
- Reporting window: HH:MM–HH:MM TZ

## Message Counts
- Person A: N messages, first–last time

## Topics by Thread
### thread-name (#parent-channel)
- Messages: N; participants: A, B; time span: ...
- Summary: ...
- Open questions / attention: ...
```

## Pitfalls

- **Do not rely only on guild channel listing.** Archived threads need dedicated archived-thread endpoints.
- **Do not hardcode allowed channels** if the user says to read a profile config every time.
- **Private archived threads may 403** unless the bot has permission; report this as partial coverage rather than inventing missing content.
- **Message Content Intent matters** for summaries. Without it, counts may work but topic summaries will be empty.
- **Cron script paths are relative** to Hermes' scheduler script directory; when `cronjob` rejects an absolute script path, use the filename and set `workdir` if needed.

## References

- `references/auto-thread-daily-report.md` — concrete pattern for custom auto-thread bots using `discord.allowed_channels` and Hermes cron.
