---
name: memory-management
description: Manage Hermes persistent memory and user-profile entries, especially when adding durable project/channel defaults, consolidating overlapping entries, and staying within memory character limits.
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [memory, profile, consolidation, discord, context]
---

# Memory Management

Use this skill when a task asks to remember something durable, when a memory write fails due to capacity, or when project/channel defaults need to be added without bloating persistent context.

## Triggers

- User says “remember this”, “by default”, “all conversation in this channel is about…”, or corrects a recurring preference.
- The `memory` tool reports the memory store is near or over its character limit.
- Multiple existing memory entries encode the same class of fact, such as per-channel project defaults.
- A new durable fact should survive future sessions but must be compact enough to avoid pushing out higher-value memory.

## Workflow

1. **Classify the fact before saving.**
   - Save stable user/project defaults and preferences.
   - Do not save task progress, PR numbers, issue numbers, transient errors, or one-off outcomes.

2. **Choose the right target.**
   - `target="user"` for who the user is and stable personal preferences.
   - `target="memory"` for environment/project conventions, channel defaults, and reusable contextual facts.

3. **Write declarative, compact facts.**
   - Good: `Discord project defaults: #p-komuna=Komuna; #p-video-slicer=video-slicer unless stated otherwise.`
   - Avoid imperative wording like `Always treat...`; future sessions may over-interpret it as a hard instruction.

4. **If capacity is tight, consolidate before adding.**
   - Look for entries in the same class and replace them with a single compact aggregate entry.
   - For channel/project mappings, prefer one semicolon-separated line rather than one entry per channel.
   - Remove the superseded individual entries immediately after confirming the aggregate entry contains their meaning.

5. **Retry the intended memory write or verify it was included in the consolidation.**
   - If the new fact is already included in the replacement aggregate, no separate add is needed.
   - Check the returned usage and entries for duplicate/stale facts.

## Pitfalls

- **Do not treat a full memory store as a reason to skip saving a user-requested durable fact.** Consolidate first, then save.
- **Do not preserve duplicate individual entries after creating an aggregate.** They waste scarce memory and can conflict if edited later.
- **Do not save session narratives.** Save the reusable default or preference, not the story of how it was discovered.
- **Do not use memory for procedures.** Workflows and reusable techniques belong in skills.

## References

- `references/discord-channel-defaults-consolidation.md` — example of consolidating many per-channel defaults into one compact memory entry while adding a new Discord channel mapping.
