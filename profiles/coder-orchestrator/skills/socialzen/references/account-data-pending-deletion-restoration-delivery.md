# Account & Data: pending deletion, restoration, and export delivery

Use this after the base deletion/export lifecycle exists and the remaining work is user-visible lifecycle clarity plus provider-reference preservation.

## Pending-deletion contract

- Show a dedicated pending-deletion experience instead of ordinary authenticated content.
- Display the persisted permanent-deletion timestamp and derive remaining days from that timestamp; do not invent a fresh 30-day deadline in the UI.
- Explicitly list disabled capabilities: publishing, analytics synchronization, billing renewal, and prior active sessions.
- Explain that local content/history and non-secret connected-account metadata are temporarily retained only through the grace period.

## Provider handling

- At deletion request, attempt provider-side authorization revocation where supported, clear local credentials, and mark each connection disabled.
- Preserve non-secret provider identity/reference metadata until permanent deletion so impact summaries and restoration remain coherent.
- Restoration must never restore tokens, mark providers active, resume analytics, or publish queued work. Require deliberate reconnection and make that requirement visible.
- Keep provider-specific behavior for Instagram, Facebook, and Threads; do not force all providers through one token/revocation shape.

## Lifecycle notifications

- After restoration commits, create a deduplicated Notification Center event confirming restoration and stating that social accounts must be reconnected before publishing or analytics sync can resume.
- For completed exports, expose a direct `Download Archive` action in the notification list while the archive is still valid. The action must use the authenticated short-lived grant/download flow, not a public archive URL.
- If the archive expired, was deleted, or was invalidated by deletion, remove/disable the direct action and show the truthful state.

## Verification

- Test pending-deletion date/remaining-days copy and the disabled/preserved-data disclosures.
- Test restoration notification creation and confirm provider rows remain disabled with credentials absent.
- Test completed export notification action availability and its expired/unavailable state.
- Run focused backend tests, focused frontend tests, typecheck, Go build, and production frontend build.
- Before replacing the running binary, validate all newly required startup configuration against the service environment. A successful build is not proof the deployed service can restart.
- After restart, wait for `systemctl is-active` to settle and verify the health endpoint; an `activating` result is not deployment success.

## Deployment pitfall

Account/export hardening may introduce required encryption-key configuration. Preflight the service's actual `EnvironmentFile` for a selected 32-byte export key before restart. Generate/configure secrets out of band and never print or commit them. If restart fails, inspect service status immediately, restore health, then continue frontend/public-asset verification.
