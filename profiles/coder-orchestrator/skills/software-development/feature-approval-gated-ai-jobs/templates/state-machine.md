# Transition matrix

| From | To | Guard |
|---|---|---|
| todo | queued | lane enabled, no active run |
| queued | running | conditional lane claim |
| running | review | provider completed and session/result persisted |
| running | blocked/failed | classified terminal result |
| review | todo | feedback persisted; resume same provider session |
| review | approved | reviewer and run version match |
| blocked | todo | explicit reply/requeue |

Write transition and event in one transaction. Terminal/review states release lane capacity. Startup reconciles queued/running rows against provider session state.
