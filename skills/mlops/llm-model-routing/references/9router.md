# 9router — layout, schema, diagnostics

9router is a local OpenAI-compatible router/combo gateway (user systemd unit, default port 20128).
Config points Hermes at it with `provider: custom`, `base_url: http://127.0.0.1:20128/v1`.

## Paths

| Path | What's in it |
|---|---|
| `~/.9router/db/data.sqlite` | All state: combos, API keys, usage, request details |
| `~/.9router/model-catalog.json` | Model capability catalog (vision/pdf/videoInput flags), `syncedAt`, `etag` |
| `~/.9router/model-catalog-raw.json` | Raw upstream catalog dump |
| `~/.9router/mitm/aliases.json` | Alias map (often `{}`) |
| `~/.9router/logs/` | `mitm/` only; usually empty — use `journalctl --user -u 9router` instead |
| `~/.9router/auth`, `jwt-secret`, `machine-id` | Local auth material |

## Schema (the parts that matter)

```sql
combos(id TEXT PK, name TEXT UNIQUE, kind TEXT, models TEXT/*JSON array*/, createdAt, updatedAt)
apiKeys(id, key, name, machineId, isActive, createdAt)
usageHistory(id, timestamp, provider, model, connectionId, apiKey, endpoint,
             promptTokens, completionTokens, cost, status, tokens/*JSON*/, meta)
requestDetails(id TEXT PK, timestamp, provider, model, connectionId, status, data TEXT/*JSON*/)
kv(scope, key, value, type, data)      -- e.g. customModels|<alias>|<id>|llm
settings(id, data/*JSON*/)             -- app config incl. capacityAdapter/ponytailEnabled
_meta(key, value)                      -- schemaVersion, appVersion, totalRequestsLifetime
providerConnections, providerNodes, proxyPools, usageDaily
```

Alias naming convention: `ocg/` = opencode-go, `cx/` = codex, `oc/` = opencode; bare names are
direct provider models.

## Diagnostics

**Which model actually served traffic** (authoritative, per request):

```bash
sqlite3 ~/.9router/db/data.sqlite \
  "select timestamp,provider,model,cost from usageHistory order by timestamp desc limit 15;"

# counts per model over a window — shows whether a combo is really round-robining
sqlite3 ~/.9router/db/data.sqlite \
  "select provider,model,count(*) from usageHistory where timestamp > '2026-09-12T22:42' group by 1,2;"
```

**Combos (alias → members):**

```bash
sqlite3 ~/.9router/db/data.sqlite "select name, models from combos;"
```

**Full request/response pairs** (prompt preview, latency ttft/total, token details):
`requestDetails.data` holds JSON; `request.providerRequest._preview` is truncated but shows the
upstream model + first user message. Note `requestDetails` is a **rolling buffer of ~1000 rows** —
`max(timestamp)` can lag hours behind `usageHistory`, so don't use it to answer "what just ran".

**Live resolution:** `scripts/resolve_combo.py <alias> http://127.0.0.1:20128`

## The router reaps its own port on startup

`cli.js` calls `killAllAppProcesses(port)` then `killProcessOnPort(port)` **before binding**, i.e.
it SIGKILLs whatever currently owns the port. Consequence: if a second copy of 9router is ever
running (another systemd unit at a different scope, a manual launch, a stray `next-server`), the
two kill each other in a loop — each restart revives one copy, which kills the other. Symptoms:
intermittent client `APIConnectionError` plus `status=9/KILL` in the unit journal every restart
interval. Check for duplicate instances *before* blaming `localhost`/IPv6 resolution; full
procedure in the `systemd` skill → `references/duplicate-unit-conflicts.md`.

## Notes / traps

- Router answers with `Content-Type: text/event-stream` even for non-stream requests, body shaped
  `{...json...}data: [DONE]`. Plain `json.load()` fails with `Extra data: line 1 column N`.
- Combo members can be **free or vision-only** models; a non-vision primary means image/PDF input
  gets rerouted by the `capacityAdapter` in `settings`, so the serving model can differ per request.
- `cost: "0"` on `*-free` upstreams is normal.
- API key stored in `apiKeys` is shared with Hermes (`~/.hermes/.env` `OPENAI_API_KEY`), and
  `usageHistory.apiKey` records the masked form (`sk-xxx...yyyy`).
