# Legacy skill package: `discord-gateway-routing`

This file preserves the former `discord-gateway-routing` SKILL.md after consolidation into `hermes-operations`. Relative support-file links have been rewritten to the re-homed files under `hermes-operations`.

---

---
name: discord-gateway-routing
description: Diagnose and explain Hermes Discord gateway routing, sessions, reply targets, auto-threading, free-response channels, and thread behavior.
version: 1.0.0
created_by: agent
platforms: [linux, macos]
metadata:
  hermes:
    tags: [hermes, discord, gateway, routing, threads, troubleshooting]
---

# Discord Gateway Routing

Use this when a user asks why Hermes replied in a channel instead of a thread, why auto-threading did or did not happen, why a Discord message was ignored, or how Discord gateway config maps to runtime behavior.

## Fast workflow

1. **Check effective config first**
   - Active profile config usually lives at `~/.hermes/profiles/<profile>/config.yaml`.
   - Also check root `~/.hermes/config.yaml` if the gateway might be running from the default profile.
   - Inspect the `discord:` block for: `require_mention`, `thread_require_mention`, `free_response_channels`, `allowed_channels`, `ignored_channels`, `no_thread_channels`, `auto_thread`, and `history_backfill`.

2. **Check gateway logs for the real routed target**
   - Look in the active profile's `logs/gateway.log` first.
   - Key log lines include `inbound message`, `response ready`, and `Sending response`.
   - The `chat=` ID tells whether Hermes saw a parent channel or thread.

3. **Explain using adapter conditions, not guesses**
   - Discord auto-threading is config-driven but may be bypassed by channel state.
   - Free-response channels are designed for inline lightweight chat; auto-threading is skipped there by adapter logic.
   - Existing Discord reply messages may be skipped for auto-thread creation.
   - Threads have their own session namespace; parent channels and threads are not interchangeable.

4. **Be direct with user-facing wording**
   - If the config says `auto_thread: true` but another condition suppresses it, say that plainly.
   - Do not claim Hermes lacks Discord thread capability if config/code show it can create or route threads.
   - Keep the answer concise and cite the exact condition that caused the behavior.

## Common pitfall: `auto_thread: true` does not always create a thread

In the Discord adapter, auto-threading can be skipped when the current channel is configured as a free-response channel, listed in no-thread channels, is voice-linked, or the incoming message is itself a Discord reply. See `references/discord-gateway-routing-auto-thread-free-response.md` for the concrete diagnostic pattern.

## Verification checklist

- Confirm which profile gateway is active.
- Confirm the channel ID from logs matches the configured ID.
- Confirm whether the message was in a thread, parent channel, DM, or Discord reply.
- Confirm whether `free_response_channels` or `no_thread_channels` includes the channel/parent ID.
- If behavior should change, propose the config/code change rather than insisting the user manually create threads.