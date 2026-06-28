# Discord channel defaults memory consolidation

Session pattern captured: the user asked to add a Discord channel as an allowed channel and remember that all conversation there defaults to a specific project.

## Useful approach

When persistent memory is nearly full and already contains several one-entry-per-channel project defaults:

1. Add or update the operational config separately.
2. Attempt the memory write for the new default.
3. If the write fails due to the memory character limit, replace the oldest matching per-channel default entry with a compact aggregate, for example:

   ```text
   Discord project defaults: #p-socialzen=SocialZen; #p-boilerplate=boilerplate; #p-komuna=Komuna; #p-komuna-old=komuna-old; #p-video-slicer=video-slicer; <#CHANNEL_ID>=project-name unless stated otherwise.
   ```

4. Remove the now-duplicated individual channel-default entries.
5. Verify the returned memory entries still include every channel mapping and that usage dropped enough for future additions.

## Why this matters

Per-channel defaults are durable and valuable, but each one as a separate full sentence wastes memory. A single mapping-style entry preserves semantics and gives future sessions room for higher-value facts.