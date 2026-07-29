# Preview-safe local checkout

Use when an isolated functional preview has no payment-provider sandbox credentials but must demonstrate checkout through entitlement delivery.

## Contract

- Require an explicit preview-only runtime flag; absent provider credentials must not silently enable simulation.
- Return an empty invoice URL; never redirect to a fabricated provider hostname.
- Accept simulation only on the isolated preview API/database with a dedicated callback contract.
- Route simulated completion through the canonical transactional finalizer; do not duplicate fulfillment.
- Preserve real-provider behavior whenever credentials exist.
- Repeat completion and assert one finalization, the exact snapshotted entitlement count, and one payment notification.

## Strict TDD

1. Add one handler test covering authenticated checkout, empty invoice URL, simulated completion, paid state, snapshot-derived entitlements, notification, and duplicate completion.
2. Capture the expected failure before implementation.
3. Add the smallest explicit-gate implementation.
4. Run the focused test plus callback-token and purchase-ownership regressions.
5. Restart and exercise the exact public preview chain.

## Completion boundary

Local tests, a web build, a listening API, rendered login/checkout pages, and direct finalizer calls do not prove a functional public preview. Do not send the preview as ready and ask the user to discover missing prerequisites. Exercise the exact public preview prefix with a fresh cookie jar or browser session: authenticate → establish eligible membership/package data → quote → checkout → provider sandbox payment or explicitly gated simulation → paid state → entitlement display → payment notification → action-route/return UX. Repeat completion and assert durable benefit and notification counts remain unchanged. If any step is unavailable, report code verification separately and label the preview incomplete.

Trace the running preview API logs before editing. A public checkout `502` with `xendit_not_configured` means that process lacks provider configuration; either supply genuine sandbox settings or deliberately enable the existing preview-only simulation flag. Verify the effective running-process environment after restart. Never describe simulated completion as genuine provider verification.

For SQLite previews, identify the live source DB from systemd or `/proc/<pid>/environ`, copy it with SQLite `.backup`/`VACUUM INTO`, run `PRAGMA integrity_check`, and verify `auth_users` plus eligible programs/packages/package entries before launch. A nearby database chosen by filename is not parity evidence.

## Verification tracker pitfall

When ad-hoc verification is required, create and execute the script in one shell command using `mktemp /tmp/hermes-verify-XXXXXX.sh`, a cleanup trap, and direct invocation. Avoid creating a fixed `/tmp` script via file-write tools: verification may record it as another changed path even after deletion.
