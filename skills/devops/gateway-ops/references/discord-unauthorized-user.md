# Discord: emoji-only reply / silent drop

Symptom: a Discord message appears acknowledged but the bot never generates a normal reply.

## Confirmation
```bash
grep -i 'Unauthorized user' ~/.hermes/logs/gateway.log
grep -i 'Unauthorized user' ~/.hermes/profiles/<name>/logs/gateway.log
```

If the grep hits a line like `Unauthorized user: <id> (...) on discord`, the message was dropped before the agent loop executed.

## Root causes

1. No user allowlist configured and allow-all is off.
2. Message is targeted to a thread/channel/guild not in the profile's bound targets.
3. Env/config was changed but the active gateway service was not restarted.

## Fix

For each affected profile:
- default profile: edit `~/.hermes/.env`
- named profile: edit `~/.hermes/profiles/<name>/.env`

Add:
```
GATEWAY_ALLOW_ALL_USERS=true
```

Then restart the exact profile gateway:
```bash
# default
systemctl --user restart hermes-gateway.service
# named
systemctl --user restart hermes-gateway-<name>.service
```

## Verify

```bash
systemctl --user status hermes-gateway-<name>.service
grep -i Unauthorized ~/.hermes/profiles/<name>/logs/gateway.log | tail
```

## Pitfalls

- Changing env without restart leaves the process on the old snapshot.
- Thread messages inherit parent channel restrictions; binding a parent channel does not automatically bind every child thread.
- `GATEWAY_ALLOW_ALL_USERS=true` bypasses user authorization but does not override channel/guild allowlists.
