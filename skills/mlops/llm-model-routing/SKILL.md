---
name: llm-model-routing
description: "Resolve and verify which real upstream model serves a gateway alias/combo (9router, LiteLLM-style routers), and debug routing/connection failures. Use when asked 'which model do you use / which model answered', when a config model name is an alias, or when a gateway returns APIConnectionError."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [llm, gateway, router, 9router, model-resolution, debugging, hermes-config]
---

# LLM Model Routing (alias → real upstream model)

A configured model name in an app is often an **alias or combo**, not a model. The gateway behind it decides the real upstream model per request. Never answer "which model are you" from `config.yaml` alone — resolve the alias, then confirm with one live probe.

## When to use this skill

- "Which model do you use?" / "which model actually answered that?"
- A config value like `model.default: hermes-general` needs to be turned into a real model ID.
- A gateway/routed provider returns `APIConnectionError`, retries, or empty streaming responses.
- Debugging why a specific alias routes to a model you didn't expect (or a free/vision fallback).

## Procedure

### 1. Read the app's model config

```bash
grep -A6 '^model:' ~/.hermes/config.yaml     # default / provider / base_url / api_key
```

Typical Hermes shape:

```yaml
model:
  default: "hermes-general"          # ← ALIAS, not a model
  provider: "custom"
  base_url: "http://127.0.0.1:20128/v1"
  api_key: ${OPENAI_API_KEY}         # actual value lives in ~/.hermes/.env
```

### 2. Find the gateway's own state, not just its API

A routed gateway keeps a local DB/catalog with its alias→model mapping (see `references/9router.md` for 9router's schema and paths). Reading the mapping tells you the *candidate list*; it does not tell you which one served *this* request.

### 3. Probe the gateway for the authoritative answer

`scripts/resolve_combo.py` does this in one shot:

```bash
python3 scripts/resolve_combo.py hermes-general http://127.0.0.1:20128
```

The trick: send a 5-token request for the alias and read the **`model` field of the response** — routers rewrite it to the real upstream model. Also dump combos from the router DB if present.

### 4. Confirm against what actually served traffic

The router's usage/history tables (or gateway logs) show provider + model + cost per request:

```bash
sqlite3 ~/.9router/db/data.sqlite \
  "select timestamp,provider,model,cost from usageHistory order by timestamp desc limit 15;"
journalctl --user -u 'hermes-gateway*' --since "20 min ago" | grep -i 'model='
```

Report: alias, gateway, resolved upstream model(s), and any sibling models in the combo (vision/PDF capacity fallbacks matter — a non-vision primary silently routes elsewhere for image input).

## Pitfalls

- **Alias ≠ model.** `model.default: hermes-general` is a combo name. Answering with it as if it were a model is wrong.
- **Combos have several members.** Report the primary *and* the fallback list; the member used can differ per request (round-robin, capacity adapter, vision routing).
- **`localhost` vs `127.0.0.1` — a real but frequently *wrong* first guess.** A client configured with `http://localhost:PORT` may resolve to `::1` and get `APIConnectionError` against a router bound to IPv4 only. **Test it before fixing it:**
  ```bash
  getent ahosts localhost          # does it even return ::1?
  ```
  On this host it returned `127.0.0.1` only, `http://localhost:20128` worked, and only literal
  `http://[::1]:20128` was refused — so the alias was innocent. Only change the *client's*
  `base_url` to `127.0.0.1` if the `[::1]` probe actually fails.
- **Intermittent `APIConnectionError` = suspect a duplicate router instance, not DNS.** If the
  port works from your shell but a client's calls fail in bursts, the listener is being yanked
  mid-request: a second copy of the service (system *and* user scope, or a manual launch) is
  killing it on startup. Confirm with `ss -ltnp | grep <port>`, then `ps -eo pid,ppid,etime,args`
  and check the cgroup owner (`/system.slice/…` vs `/user.slice/…`). Procedure:
  `systemd` skill → `references/duplicate-unit-conflicts.md`. Do **not** report a
  name-resolution fix for a problem you have not reproduced.
- **Gateways reply `text/event-stream` even to non-streaming requests.** `json.load(response)` then fails with `Extra data: line 1 column N`. Read the raw body and split on `data: [DONE]` before `json.loads`.
- **Don't build the probe as `curl ... -H "Authorization: Bearer $(grep ...)"`.** Command-substitution-laden curl one-liners get rejected by the agent's hardline command parser. Use `execute_code` (urllib) or the bundled script instead.
- **Cheap/free models in a combo** often show `cost: "0"` — expected for `*-free` upstreams, not a routing bug.
- Don't confuse *your* serving model with another service's errors in the same log: check the `thread=`/`model=` fields on each log line before blaming your own path.

## Verification

One runnable check: `python3 scripts/resolve_combo.py <alias> <base_url>` must print a `model:` that is a real upstream ID, and the same model should appear in `usageHistory` for the matching timestamp.

## References

- `references/9router.md` — 9router paths, SQLite schema (combos, usageHistory, requestDetails, kv/customModels), and diagnostics recipes
