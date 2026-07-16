---
name: hermes-discord-channels
description: "Manage Discord channel access and whitelisting for multi-profile Hermes deployments."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, discord, whitelist, multi-profile, gateway, channel]
    related_skills: [hermes-agent, hermes-servicemanagement]
---

# Hermes Discord Channel Management

Manage Discord channel access for a specific Hermes profile. Covers discovery,
adding/removing channels from `discord.allowed_channels`, distinguishing parent
channels from threads, and restarting named-profile gateways.

Use when the user says things like:

- "add this channel to allowed channels for <profile>"
- "allow the bot in <channel>"
- "make the orchestrator respond in this thread"
- "remove <channel> from the whitelist"

## Prerequisites

- The target Hermes profile uses a Discord-enabled gateway.
- You have access to both the source config and runtime config paths listed
  below.

## Config locations (MUST update both)

| Location | Role |
|-|-|
| `~/hermes-config/profiles/<profile>/config.yaml` | Source / ops-root config of truth |
| `~/.hermes/profiles/<profile>/config.yaml` | Runtime config consumed by the gateway |

`hermes-agent` skill reference: `references/discord-channel-whitelist.md`.

**Pitfall:** If source and runtime drift, the next gateway restart reverts
changes or loads stale values. Add the ID to the source file first, then copy
the same change to the runtime file.

## Step-by-step

1. Identify the channel/thread IDs. Canonical source is
   `~/.hermes/profiles/<profile>/channel_directory.json`, which uses the shape:

   ```json
   {
     "updated_at": "<iso timestamp>",
     "platforms": {
       "discord": [
         {
           "id": "<channel_id>",
           "name": "<name>",
           "guild": "<guild>",
           "type": "channel | group | thread",
           "thread_id": "..."
         }
       ]
     }
   }
   ```

   **Pitfall:** this is NOT a flat list. The `discord` entries live under
   `platforms.discord`. Do not iterate the top-level dict keys as channels.

2. Determine whether you need the parent channel ID, the thread ID, or both:
   - To respond in a text channel: add the channel ID.
   - To respond inside a thread: add `parent_channel_id:thread_id` and set
     `auto_thread: true`.
   - For threads, discovery keys may appear as `parent_id:thread_id` in
     `channel_directory.json`.

3. Update `discord.allowed_channels`:
   - Source config often uses a quoted comma-separated scalar string.
   - Runtime config usually uses a YAML list; thread entries are written as
     bare `channel:thread` mappings (unquoted), channel IDs are quoted
     strings.

4. Propagate the same change to the runtime config.

5. Restart the profile gateway:

   ```bash
   systemctl --user restart hermes-gateway-<profile>.service
   ```

   **Pitfall:** SIGTERM frequently hangs in `deactivating (stop-sigterm)`
   because Python asyncio delays shutdown for active tasks. If status stays in
   `stop-sigterm` longer than ~90 seconds:

   ```bash
   kill -9 <old-pid>
   systemctl --user daemon-reload
   systemctl --user start hermes-gateway-<profile>.service
   ```

   **Pitfall:** do not use `hermes gateway restart` from inside the gateway;
   it is blocked to prevent restart loops.

6. Verify:
   - `systemctl --user status hermes-gateway-<profile>.service` → active.
   - Check profile logs:
     `~/.hermes/profiles/<profile>/logs/gateway.log`
   - Send a message in the target channel; the bot should respond.

## `free_response_channels` vs `allowed_channels`

- `allowed_channels` is a whitelist. The bot ignores all channels not listed.
- `free_response_channels` lets the bot respond without `require_mention`
   even if the channel is not otherwise whitelisted.
- For a dedicated profile (e.g. `coder-orchestrator`), set
  `require_mention: false` and rely on `allowed_channels` only.

## Verification checklist

- [ ] Mapped the correct channel/thread IDs from `channel_directory.json`.
- [ ] Added parent channel and/or `channel:thread` entry, depending on
      thread support configuration.
- [ ] Updated both source (`~/hermes-config/…`) and runtime
      (`~/.hermes/profiles/…`) config files.
- [ ] Restarted gateway using `systemctl --user restart …` (or kill-9 path
      if SIGTERM hung).
- [ ] Confirmed `active (running)` and checked recent gateway log entries.
- [ ] Tested with a real message in the target channel/thread.

## References

- `references/config-sync.md` — source vs runtime config sync pattern

## Related class-level skills

- `hermes-agent` / `references/discord-channel-whitelist.md` — bundled
  reference on Discord adapter behavior, `require_mention`, `channel_prompts`,
  and gateway restart semantics.

## Captured patterns

- `channel_directory.json` schema: `{"updated_at": "…", "platforms": {"discord": [...]}}`.
  Do not iterate the top-level object keys as channels; entries live under
  `platforms.discord`.
- Thread entries in `discord.allowed_channels` are unquoted `parent:thread`
  mappings in runtime YAML lists, but appear as quoted comma-joined strings in
  source-of-truth configs.
- SIGTERM hang recovery: kill -9 old PID, `systemctl --user daemon-reload`,
  `systemctl --user start`.
