# Auto-thread skipped in free-response channels

Session diagnostic pattern from a Discord gateway conversation:

## Symptom

User says Hermes should create a new Discord thread because config has:

```yaml
discord:
  auto_thread: true
```

But Hermes replies inline in the channel.

## Checks that resolved it

1. Inspect active profile config and root config if needed.
2. Confirm the channel ID in logs (`chat=<id>`) matches the configured channel.
3. Look for `free_response_channels` and `no_thread_channels`.

Observed config pattern:

```yaml
discord:
  require_mention: false
  free_response_channels: '<channel_id>'
  allowed_channels: '<channel_id>'
  auto_thread: true
  thread_require_mention: false
```

## Adapter behavior

The Discord adapter computes:

```py
skip_thread = bool(channel_ids & no_thread_channels) or is_free_channel
...
if auto_thread and not skip_thread and not is_voice_linked_channel and not is_reply_message:
    thread = await self._auto_create_thread(message)
```

So `auto_thread: true` is bypassed in free-response channels. The adapter also skips auto-thread creation for Discord reply messages:

```py
is_reply_message = getattr(message, 'type', None) == discord.MessageType.reply
```

## User-facing explanation

Say: "`auto_thread: true` is set, but this channel is configured as a free-response channel, and the Discord adapter skips auto-threading for free-response channels. It may also skip when the incoming message is a Discord reply."

Avoid saying: "I cannot create threads" unless the live adapter/config truly lacks thread capability. Hermes can create threads; this case is conditional suppression.