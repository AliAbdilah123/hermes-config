# iptables port-name translation pitfall

## Symptom
`iptables -L INPUT -v --line-numbers` shows numeric ports as `udp dpt:mxit` even though commands used `--dport 9119`.

## Impact
Rule deletion must match the stored spec exactly. Using the numeric form when the stored form is a name can leave stale rules behind.

## Reliable workflow
1. Inspect stored rules first:
   `sudo iptables -L INPUT -v --line-numbers --numeric`
2. Copy the rule spec from that output verbatim for delete.
3. If names are resolved, delete using the shown service name.
4. Delete failed attempts before reinserting, to avoid duplicate rules.

## Session example (2026-05-31)
Port 9119 appeared as `mxit` in INPUT rules. Deleting with `--dport 9119` did not remove the existing rule. Re-adding without cleanup produced duplicate ACCEPT rules for tailscale0 and duplicate DROP rules for all interfaces.