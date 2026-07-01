# Social publishing OAuth + false-published triage

Use this when a social scheduler reports posts as `PUBLISHED` but they do not appear on Facebook/Instagram, or when connecting one provider makes another provider appear connected.

## Checks

1. **Trace status transitions before provider code.** Search for background/GET/list handlers that update scheduled posts without making provider API calls. A common bug is a convenience auto-publish update such as `UPDATE posts SET status='PUBLISHED'` in a read handler or scheduler stub.
2. **Separate parent post status from per-platform target status.** Only mark the parent `PUBLISHED` if every required `post_targets` row succeeded. If a target fails, store provider error in `post_targets.error_message` and avoid billing/quota increments that count parent `PUBLISHED` blindly.
3. **Verify credentials needed for real publish are persisted.** Instagram media publish needs an IG user id plus a usable access token. If the account table only stores id/username/expiry, publishing cannot work; fail truthfully and require reconnect after adding token storage.
4. **Do not auto-create Instagram accounts from Facebook connect unless product explicitly wants that.** Facebook Pages may expose `instagram_business_account`, but inserting it into the same `instagram_accounts` list makes the UI think Instagram was connected directly and can cause duplicate/wrong account selection. Save Facebook Pages separately; require explicit Instagram connect for IG publishing.
5. **Use the provider's real publish success signal.** For Instagram images: create a media container, then call `media_publish`; mark success only when the publish response includes a media id. For Facebook: publish to the real external `page_id`, not the local DB row id.
6. **Token expiry UX must follow stored token reality.** If short-lived OAuth tokens are exchanged for long-lived tokens, store the long-lived token and returned expiry. If exchange fails, use a conservative fallback and show reconnect only when the stored expiry is actually near/after expiry.

## Minimal verification

- Unit-test that an empty/no-op publisher does not fake success.
- Inspect DB schema for required token columns before claiming real publish works.
- Trigger/observe the scheduler interval from service logs or status after deploy.
- Public app health and SPA HTTP 200 are not enough; check provider target rows/errors when possible.
