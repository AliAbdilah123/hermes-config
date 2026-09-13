# "The bot isn't responding in this channel" — triage

Three different root causes present with the same complaint. Check them in
order; the fix for (2) and (3) is **not** editing `allowed_channels`.

## 1. Channel/thread genuinely not whitelisted

- Confirm the ID exists in `discord.allowed_channels` in **both** the source
  (`~/hermes-config/profiles/<profile>/config.yaml`) and runtime
  (`~/.hermes/profiles/<profile>/config.yaml`) configs.
- Add it, then restart (see `scripts/restart-gateway.sh`).

## 2. Whitelisted but the gateway is dead or auth-failed

Symptom: the bot has an entry, maybe even a `channel_directory.json` record,
but the last messages in the channel are bot errors, e.g.

```
⚠️ Provider authentication failed. Check the configured credentials;
raw provider details are in the gateway logs.
```

That is *not* a whitelist problem. Do not start editing config — check state
and restart:

```bash
systemctl --user is-active hermes-gateway-<profile>.service
tail -40 ~/.hermes/profiles/<profile>/logs/gateway.log
```

Healthy restart markers in the log:

```
[Discord] Connected as <BotName>#<discriminator>
✓ discord connected
Gateway running with N platform(s)
```

Restart with `terminal(background=true)` + `process(action="wait", …)` — see
the SKILL.md workaround section.

## 3. Message never triggered the bot

- `require_mention: true` in the profile's `discord` block and the message
  carried no mention → nothing runs.
- `thread_require_mention: false` + `auto_thread: true` is the usual setup for
  dedicated agents (e.g. `coder-orchestrator`): `require_mention: false`, rely
  on `allowed_channels` only.
- The user posted in the **parent channel** while only
  `parent:thread` is whitelisted (or vice versa). The two are distinct
  entries; add both if the bot should answer in each.

## Reading the channel directory correctly

`channel_directory.json` is the ID source of truth, but its `name` for a
thread is auto-generated from the first user message, so an entry like
`"Ali's workflow / #p-light-pos / add this channel as allowed channel for /
topic 1548262634825056287"` proves only that a thread exists — **not** that the
bot ever answered in it. Match against real messages.

Thread keys appear as `"<parent_id>:<thread_id>"` with `thread_id` mirrored:

```json
{"id": "1548262198306938910:1548262634825056287",
 "name": "… / #p-light-pos / … / topic 1548262634825056287",
 "type": "thread", "thread_id": "1548262634825056287"}
```

The parent channel (`1548262198306938910` here) is a normal
`"type": "channel"` entry elsewhere in the same list.

## Resolving a bot mention to a profile

The user often writes `<@1497601456684011622>` instead of a profile name:

```
discord_admin(action='member_info', guild_id='<guild>',
              user_id='1497601456684011622')
# -> {"username": "Coder Assistant", "bot": true, ...}
```

Map the username to the profile directory: "Coder Assistant" →
`coder-orchestrator`, "General Assistant" → `default`. Verify by grepping the
profile configs for the bot's channel IDs rather than guessing.

## Editing the two config shapes

Same channel, two syntaxes — see also `references/config-sync.md`.

| Config | Shape |
|-|-|
| source (`~/hermes-config/…`) | one quoted comma-separated scalar |
| runtime (`~/.hermes/profiles/…`) | YAML list; quoted strings for plain channels, bare `parent:thread` for threads |

Source:

```yaml
  allowed_channels: '1510322701141803199,1546372050929721344,1548262198306938910,1548262198306938910:1548262634825056287'
```

Runtime:

```yaml
  allowed_channels:
    - '1510322701141803199'
    - '1548262198306938910'
    - 1548262198306938910:1548262634825056287
```

Note the sibling agents may also be writing these files; the patch tool warns
if the file changed since you read it. Re-read before writing when that fires.
