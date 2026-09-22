# Meta Instagram webhook recipient routing

Use this when signed Instagram DM webhooks return `200` but messages never reach the note/message insert path.

## Trace the real identifier without remapping

Instrument these boundaries with the message ID as correlation key:

1. Raw webhook: `entry.id`, `messaging[].recipient.id`, `sender.id`, `message.mid`.
2. Handler dispatch: the exact `recipientID` passed to the domain/store function.
3. Integration lookup: whether `instagram_integrations.instagram_user_id = recipientID AND status = 'active'` matched.
4. Persistence: inserted/deduplicated note/message ID and nullable social identity.

Pass webhook `recipient.id` unchanged to the domain/store validation boundary. Do not replace it with an environment-configured account ID before lookup. Do not reject solely because `entry.id` differs unless Meta's current contract guarantees both fields use the same identifier type.

## Configuration and startup trap

Trace startup wiring too. A startup helper may overwrite the integration row from environment configuration, making the DB correct before restart but mismatched afterward. Verify independently:

- effective runtime account ID,
- active integration row after restart,
- incoming webhook `recipient.id` from live logs.

They must converge on the webhook recipient ID. Correct configuration rather than adding schema coupling or hardcoding a username.

## Unmatched sender behavior

Validate the recipient/inbox first. Once it matches an active integration, an unknown sender may route to that integration's dedicated owner with `social_identity_id = NULL`. If the recipient itself is unknown, acknowledge safely and do not route it through another configured inbox owner.

## Regression matrix

Add an HTTP test where the configured account ID intentionally differs from the webhook recipient, `entry.id` may differ from `recipient.id`, and an active integration exists for the webhook recipient. Require persistence under that integration's owner. Also assert an unknown recipient creates no note and does not cause a server error. Test the store/domain function directly for active and inactive rows.

## Live verification boundary

A signed synthetic webhook proves application routing, not Meta delivery. Fresh-provider E2E requires:

- a new Meta POST in reverse-proxy access logs,
- application logs showing `recipient.id -> recipientID -> active integration -> insert`,
- the exact unique DM text/message ID persisted.

If no provider POST arrives after a fresh DM, stop code changes and inspect Meta webhook subscription, selected Instagram account, app mode/roles, and token/account pairing. A successful Graph read and HTTP health check do not prove webhook delivery.
