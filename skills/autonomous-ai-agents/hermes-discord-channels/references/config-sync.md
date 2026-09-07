# Source vs Runtime Discord Config Sync

Hermes multi-profile deployments typically keep two copies of each profile config:

- `~/hermes-config/profiles/<profile>/config.yaml` — ops source of truth
- `~/.hermes/profiles/<profile>/config.yaml` — runtime config consumed by the gateway

## Why both matter

`discord.allowed_channels` must be updated in **both** files or the next gateway restart reverts runtime state back to the source copy.

## Shape differences

| Config | Typical shape for `allowed_channels` |
|---|---|
| Source (`~/hermes-config/...`) | Often a **quoted comma-joined string** |
| Runtime (`~/.hermes/profiles/...`) | Usually a **YAML list**; threads are `parent:thread` mappings |

When editing source configs that use quoted scalar strings, avoid introducing YAML list syntax unless the file already uses it — otherwise parsing fails at runtime.

## Sync pattern

1. Edit the source config first.
2. Mirror the same IDs into the runtime config, preserving its existing YAML shape.
3. Restart the profile gateway from outside the Hermes process.

## Channel/thread ID forms

- Parent channel: `'1234567890'`
- Thread: `parent_channel_id:thread_id`
- Same channel as both parent and thread member: add both forms if needed.

## Restart quirk

Restart commands run from inside the gateway session are broadly blocked, not just `hermes gateway restart`. Wrappers like background terminal sessions, `bash -lc`, `nohup`, `setsid`, and local ssh loops can still inherit the gateway’s restart-loop protection and fail. Run `systemctl --user restart hermes-gateway-<profile>.service` from an external shell instead.
