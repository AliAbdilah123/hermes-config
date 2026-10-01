# Instagram webhook runtime observability

Use when a real DM must be correlated with the webhook payload and downstream processing.

## Safe observation sequence

1. Follow the production service journal from a clean timestamp and watch for the final webhook summary.
2. For each match, query a narrow surrounding time window and correlate these lines:
   - `webhook receipt`
   - `webhook event` (`sender`, `recipient`, `message`)
   - `webhook dispatch`
   - `dm integration result`
   - `inbox lookup result`
   - final `webhook result`
3. Do not infer raw IDs from a summary line alone. `processed=1` means the event passed the handler, but the integration-result line is the stronger evidence that `ProcessInstagramDM` ran and whether it matched.
4. Distinguish event classes:
   - `echo=1`: outbound API message reflected by Meta; no inbound DM processing.
   - `missing_text=1`: non-text/unsupported event; no DM processing.
   - `signature_invalid`: untrusted request; payload must not be inspected or processed.
   - `dm integration result=matched status=active`: inbound text reached the domain processor and matched an active integration.
   - `unmatched` / `no_integration`: processor ran, but recipient/sender routing did not resolve.
5. Correlate suppressed watch notifications by reading the journal directly for the whole interval; rate-limited watcher output is not a complete event ledger.

## Raw-ID diagnostic boundary

Identifier logs may be one-way truncated hashes. Never label them as exact `sender.id`, `recipient.id`, or `message.mid`, and do not claim they can be recovered. Report them explicitly as hashes.

If exact IDs are temporarily required:

1. Keep message text, signatures, secrets, and access tokens redacted.
2. Add narrowly scoped temporary raw-ID logging only for `sender.id`, `recipient.id`, and `message.mid`, with a clear removal condition.
3. Test the logger, rebuild the exact binary named by systemd `ExecStart`, install it, restart the service, and verify a runtime marker proves the new binary is active. Source state and a successful restart do not prove the deployed binary contains the change.
4. Capture one real inbound DM. Outbound API sends generate echoes and do not prove inbound sender identity.
5. Remove raw-ID logging immediately after capture, rebuild/restart again, and verify redaction is restored.

## Token handling

Never print, quote, store in scripts, or reuse a token pasted into chat. Treat it as compromised, ask the user to revoke/rotate it, and use the service's existing secret injection only after rotation. Never expose or modify a token merely to inspect webhook logs.

## Reporting shape

Report only:

- exact ID or clearly labeled hash
- whether `ProcessInstagramDM` was called
- matched/unmatched/ignored reason
- timestamp and timezone

Avoid repeating unchanged explanations across a stream of events; summarize multiple events in a compact table when useful.
