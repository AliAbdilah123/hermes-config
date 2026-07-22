# code-server config gotcha: `default:` is not a valid key

This is a repeatable failure mode when creating a systemd service for code-server.

## Symptom
```
error error reading /home/ubuntu/.config/code-server/config.yaml: Unknown option --default=/workspace
```

## Cause
`default:` is not a valid key in `config.yaml`. The first positional CLI argument to `code-server` is the directory to open; there is no config-file key for it.

## Fix
1. Remove the `default:` line from `config.yaml`.
2. Pass the directory as a positional `<path>` argument to `ExecStart`:

```
ExecStart=/usr/bin/code-server --bind-addr 0.0.0.0:8999 /home/ubuntu
```

## Verified config
```yaml
bind-addr: 0.0.0.0:8999
auth: password
password: password
cert: false
```

## Unit pattern
- `--bind-addr` takes precedence over config-file values and `$PORT`.
- First run writes a fresh `config.yaml` with `127.0.0.1:8080`; always edit the address to match the unit.
