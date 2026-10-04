# Notification delivery milestones

Use this checklist for notification milestones spanning API, persistence, UI, browser permission, and email delivery.

## Acceptance slices

Test each slice RED before implementation:

1. **Inbox:** create an event through the real message API, list notifications, mark one read, and prove another user cannot see private-channel notifications.
2. **Preferences:** round-trip in-app/browser/email flags, timezone, DND start/end, and mention override. Reject invalid IANA zones, malformed clocks, and half-configured DND windows.
3. **Mute semantics:** muted channels suppress ordinary delivery; an explicit mention may bypass mute only when the stored override allows it. Avoid duplicate visible entries when one message contains both a direct mention and a channel mention.
4. **DND:** inject explicit UTC instants and test local start (inclusive), local end (exclusive), overnight windows, and mention override. Use IANA timezone conversion, not fixed offsets.
5. **Email:** persist an outbox row with a unique event/delivery key, make the SMTP boundary minimal, test transient failure then retry, and prove a sent row is not sent again.
6. **UI:** test opening the inbox, changing preferences, muting the active channel, and requesting browser permission. Tests must accept denied/default permission; OS permission is not an acceptance prerequisite.

## Implementation boundaries

- Authorize inbox reads against current workspace/channel/conversation access, not merely the notification row's owner.
- Keep browser permission user-triggered and degrade cleanly when unavailable or denied.
- Persist retries and dedupe in the database; process due outbox rows outside request handling.
- A digest is batching by recipient/time window, not merely an email whose subject says “digest.” If batching is required, test multiple events collapsing into one delivery.
- Exactly-once claims require both a unique enqueue key and a concurrency-safe claim/send transition. A `sent_at IS NULL` update after SMTP protects display state but does not by itself prevent two workers from sending concurrently.

## Verification

After the last edit, run focused notification tests plus the owning backend and frontend checks. If the harness reports that no canonical command was detected, create an OS-safe `mktemp /tmp/hermes-verify-<project>-XXXXXX` script, execute all focused checks from it, remove it, and report the evidence explicitly as **ad-hoc**, not canonical suite green.
